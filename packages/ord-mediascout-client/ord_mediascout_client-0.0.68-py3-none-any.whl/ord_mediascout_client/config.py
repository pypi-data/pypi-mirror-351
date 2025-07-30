import dotenv
from pydantic.env_settings import BaseSettings
from pydantic.fields import Field

dotenv.load_dotenv()


class ORDMediascoutConfig(BaseSettings):
    class Config:
        case_sensitive = True

    url: str = Field(..., env='URL')
    username: str = Field(..., env='MEDIASCOUT_USERNAME')
    password: str = Field(..., env='MEDIASCOUT_PASSWORD')
