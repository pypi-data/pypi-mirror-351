from pydantic import BaseModel, Field
from typing import List


class GetSupplierByCategoryOptions(BaseModel):
    idx: int = Field(alias="id")
    categoryId: int = Field(alias="categoryId")
    name: str


class GetSupplierByCategoryPayload(BaseModel):
    idx: int = Field(alias="id", default=None)
    value: List[GetSupplierByCategoryOptions] = None
    categoryId: int = Field(alias="categoryId")
    name: str


class GetSupplierByCategoryResponse(BaseModel):
    description: str
    payload: List[GetSupplierByCategoryPayload]
