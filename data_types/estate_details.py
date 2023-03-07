from pydantic import BaseModel, validator


class EstateDetails(BaseModel):
    price: str
    size: str
    location: str

    @validator("price", pre=True)
    def validate_price(cls, price: str) -> str:
        return price.replace(" zł", "")

    @validator("size", pre=True)
    def validate_size(cls, size: str) -> str:
        return size.replace(" m²", "")

    class Config:
        allow_extra = False
