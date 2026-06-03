# app/app.py
from fastapi import FastAPI, Depends
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from lifespan import lifespan
from dependencies import get_db_session
from services import add_item, get_item, update_item, delete_item, get_item_by_qs
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

@app.get('/advertisement',
         response_model=schemas.GetAdvResponse,
         summary='Получить объявление по полям')
async def get_adv_by_qs(
        query_string: str,
        session: SessionDep
):
    advs = await get_item_by_qs(session, models.Advertisement, query_string)
    return [schemas.GetAdvResponse(**adv.to_dict()) for adv in advs]


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