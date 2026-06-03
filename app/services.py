# app/services.py
from asyncpg.exceptions import UniqueViolationError
from fastapi import HTTPException, status
from sqlalchemy import select, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

import models
import schemas


async def add_item(
        session: AsyncSession,
        orm_model: type[models.Advertisement],
        adv_data: schemas.CreateAdvRequest
) -> models.Advertisement:
    new_adv = orm_model(**adv_data.model_dump())
    session.add(new_adv)
    try:
        await session.commit()
        await session.refresh(new_adv)
        return new_adv
    except IntegrityError as e:
        await session.rollback()
        # Проверяем, является ли ошибка нарушением уникальности (код 23505 для PostgreSQL)
        if isinstance(e.orig, UniqueViolationError) and e.orig.pgcode == '23505':
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Item with such data already exists."
            )
        else:
            # Если это другая ошибка целостности, пробрасываем её дальше
            raise e


async def get_item(
        session: AsyncSession,
        orm_model: type[models.Advertisement],
        adv_id: int
) -> models.Advertisement:
    stmt = select(orm_model).where(orm_model.id == adv_id)
    result = await session.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{orm_model.__name__} with id {adv_id} not found"
        )
    return item

async def get_item_by_qs(
        session: AsyncSession,
        orm_model: type[models.Advertisement],
        query_string: str
) -> list[models.Advertisement]:
    search_pattern = f"%{query_string}%"
    conditions = [
        orm_model.title.ilike(search_pattern),
        orm_model.description.ilike(search_pattern),
        orm_model.owner.ilike(search_pattern),
    ]
    if query_string.isdigit():
        conditions.append(orm_model.price == int(query_string))
    stmt = select(orm_model).where(or_(*conditions))
    result = await session.execute(stmt)
    items = result.scalars().all()
    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{orm_model.__name__} with query string {query_string} not found"
        )
    return list(items)

async def update_item(
        session: AsyncSession,
        orm_model: type[models.Advertisement],
        adv_id: int,
        update_data: schemas.UpdateAdvRequest
) -> models.Advertisement:
    """
    Обновляет запись. Если done=True, автоматически проставляет finish_time.
    """
    item = await get_item(session, orm_model, adv_id)

    # Преобразуем update_data в словарь, исключая поля со значением None
    update_dict = update_data.model_dump(exclude_unset=True)

    for key, value in update_dict.items():
        setattr(item, key, value)

    await session.commit()
    await session.refresh(item)
    return item


async def delete_item(
        session: AsyncSession,
        orm_model: type[models.Advertisement],
        adv_id: int
) -> None:
    """
    Удаляет запись.
    """
    item = await get_item(session, orm_model, adv_id)
    await session.delete(item)
    await session.commit()
