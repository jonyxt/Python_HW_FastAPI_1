# app/app.py
from fastapi import FastAPI, Depends, Query
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from datetime import date
from lifespan import lifespan
from dependencies import get_db_session
from services import add_item, get_item, update_item, delete_item, search_items
import models, schemas


app = FastAPI(
    title='FastAPI_1',
    description='Сервис объявлений купли/продажи',
    version='0.0.1',
    lifespan=lifespan
)

SessionDep = Annotated[AsyncSession, Depends(get_db_session)]

@app.post("/advertisement", response_model=schemas.CreateAdvResponse, summary="Создать новое объявление")
async def create_adv(
        adv_data: schemas.CreateAdvRequest,
        session: SessionDep
):
    # Используем сервисную функцию
    new_adv = await add_item(session, models.Advertisement, adv_data)
    return schemas.CreateAdvResponse(id=new_adv.id)

@app.get(
    "/advertisement",
    response_model=list[schemas.GetAdvResponse],
    summary="Поиск объявлений по полям",
)
async def search_adv(
        session: SessionDep,
        title: str | None = Query(default=None),
        description: str | None = Query(default=None),
        price: int | None = Query(default=None),
        owner: str | None = Query(default=None),
        created_at: date | None = Query(default=None),
):
    advs = await search_items(
        session=session,
        orm_model=models.Advertisement,
        title=title,
        description=description,
        price=price,
        owner=owner,
        created_at=created_at,
    )

    return [schemas.GetAdvResponse(**adv.to_dict()) for adv in advs]

@app.get("/advertisement/{advertisement_id}",
         response_model=schemas.GetAdvResponse,
         summary="Получить объявление по ID"
         )
async def get_adv(
        advertisement_id: int,
        session: SessionDep
):
    adv = await get_item(session, models.Advertisement, advertisement_id)
    # Преобразуем ORM-модель в словарь и затем в Pydantic-схему
    return schemas.GetAdvResponse(**adv.to_dict())

@app.patch("/advertisement/{advertisement_id}", response_model=schemas.UpdateAdvResponse, summary="Обновить объявление")
async def update_adv(
        advertisement_id: int,
        update_data: schemas.UpdateAdvRequest,
        session: SessionDep
):
    updated_adv = await update_item(session, models.Advertisement, advertisement_id, update_data)
    return schemas.UpdateAdvResponse(**updated_adv.to_dict())


@app.delete("/advertisement/{advertisement_id}", response_model=schemas.OKResponse, summary="Удалить объявление")
async def delete_adv(
        advertisement_id: int,
        session: SessionDep
):
    await delete_item(session, models.Advertisement, advertisement_id)
    return schemas.OKResponse()