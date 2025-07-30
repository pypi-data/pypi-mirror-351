from pydantic import BaseModel, Field, model_validator
from typing import Dict


class HomeBalanceDetails(BaseModel):
    balance: int
    # details: Dict[str, int]

    def __init__(self, **data):
        if "balance" in data:
            data["balance"] = data["balance"] // 100
        super().__init__(**data)


class HomeBalance(BaseModel):
    homeName: str
    services: Dict[str, HomeBalanceDetails] = Field(default_factory=dict)

    @model_validator(mode="before")
    def extract_services(cls, values):
        known_keys = {"homeName"}
        services = {k: v for k, v in values.items() if k not in known_keys}
        values["services"] = services
        return values
