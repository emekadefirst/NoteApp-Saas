from pydantic import BaseModel, EmailStr, Field


class AccountBaseModel(BaseModel):
    email: EmailStr
    phone_number: str = Field(..., max_length=18)
    password: str = Field(...,  max_length=128)