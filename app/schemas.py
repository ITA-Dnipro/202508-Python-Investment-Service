from pydantic import BaseModel, condecimal, Field
from typing import Optional

class InvestmentRequestCreate(BaseModel):
    project_id: int
    amount: condecimal(gt=0, max_digits=12, decimal_places=2)
    message: Optional[str] = Field(default=None, max_length=2000)

class InvestmentRequestOut(BaseModel):
    id: int
    project_id: int
    investor_id: int
    amount: float
    message: Optional[str]
    status: str

    class Config:
        from_attributes = True
