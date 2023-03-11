from pydantic import BaseModel, validator
import unicodedata


class EstateDetails(BaseModel):
    """ 
    Estate details model class.
    """
    price: str
    size: str
    location: str
    description: str

    @validator("price", pre=True)
    def validate_price(cls, price: str) -> str:
        return price.replace(" zł", "")

    @validator("size", pre=True)
    def validate_size(cls, size: str) -> str:
        return size.replace(" m²", "")
    
    @validator("description", pre=True)
    def validate_description(cls, description: str) -> str:
        des = description.replace("Oferta wysłana z programu dla biur nieruchomości ASARI CRM ()", "").replace("\n", " ")
        # Remove \xa0
        return unicodedata.normalize("NFKD", des)

    class Config:
        allow_extra = False
