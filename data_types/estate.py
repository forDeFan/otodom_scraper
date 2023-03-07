from datetime import datetime

from pydantic import BaseModel

from config.config_handler import ParametersHandler
from data_types.estate_details import EstateDetails

PARAMS = ParametersHandler().get_params()


class Estate(BaseModel):
    description: str
    url: str
    details: EstateDetails

    class Config:
        allow_extra = False
