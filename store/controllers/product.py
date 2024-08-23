from datetime import datetime
from decimal import Decimal
from email.header import Header
from typing import List, Annotated

from bson import Decimal128
from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from pydantic import UUID4

from store.core.exceptions import NotFoundException, InsertException

from store.schemas.product import ProductIn, ProductOut, ProductUpdate, ProductUpdateOut
from store.usecases.product import ProductUsecase

router = APIRouter(tags=["products"])


@router.post(path="/", status_code=status.HTTP_201_CREATED)
async def post(
    name: str, quantity: int, price: str,
    body: ProductIn = Body(...), usecase: ProductUsecase = Depends()
) -> ProductOut:
    body.name = name    # Horrível
    body.price = Decimal(price) # porém
    body.quantity = quantity # funciona
    try:
        return await usecase.create(body=body)
    except InsertException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)


@router.get(path="/{id}", status_code=status.HTTP_200_OK)
async def get(
    id: UUID4 = Path(alias="id"), usecase: ProductUsecase = Depends()
) -> ProductOut:
    try:
        return await usecase.get(id=id)
    except NotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.get(path="/", status_code=status.HTTP_200_OK)
async def query(min_value: str, max_value: str, usecase: ProductUsecase = Depends()) -> List[ProductOut]:
    return await usecase.query(min_value, max_value)


@router.patch(path="/{id}", status_code=status.HTTP_200_OK)
async def patch(
    id: UUID4 = Path(alias="id"),
    body: ProductUpdate = Body(...),
    usecase: ProductUsecase = Depends(),
) -> ProductUpdateOut:
    # O melhor seria esconder o created at do body mesmo que no final ele não altere nada
    try:
        return await usecase.update(id=id, body=body)
    except NotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)

@router.delete(path="/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    id: UUID4 = Path(alias="id"), usecase: ProductUsecase = Depends()
) -> None:
    try:
        await usecase.delete(id=id)
    except NotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
