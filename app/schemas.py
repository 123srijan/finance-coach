from datetime import date

from pydantic import BaseModel, ConfigDict


class TransactionCreate(BaseModel):
    date: date
    description: str
    amount: float
    category_id: int | None = None
    is_income: bool = False


class TransactionResponse(TransactionCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)