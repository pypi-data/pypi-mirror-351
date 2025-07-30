from typing import Optional
from pydantic import BaseModel, Field


class Brand(BaseModel):
    # id: Optional[int] = None
    name: Optional[str] = None


class MainCategory(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None


class Merchant(BaseModel):
    # id: Optional[int] = None
    name: Optional[str] = None


class Offer(BaseModel):
    original_price: Optional[int] = None
    price: Optional[int] = None
    three_month_price: Optional[int] = Field(default=None, alias="3_month_price")
    six_month_price: Optional[int] = Field(default=None, alias="6_month_price")
    nine_month_price: Optional[int] = Field(default=None, alias="9_month_price")
    twelve_month_price: Optional[int] = Field(default=None, alias="12_month_price")
    eighteen_month_price: Optional[int] = Field(default=None, alias="18_month_price")
    merchant: Optional[Merchant] = None


class ProductItem(BaseModel):
    # id: Optional[int] = None
    name_ru: Optional[str] = None
    brand: Optional[Brand] = None
    # main_categories: Optional[list[MainCategory]] = None

    offers: Optional[list[Offer]] = None
