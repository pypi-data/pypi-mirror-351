from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel

class Config(BaseSettings):
    service_token: str

    model_config = SettingsConfigDict(
        env_prefix="OP_",
        case_sensitive=False,
        extra="ignore",
    )


class FieldUpdate(BaseModel):
    title: str
    new_value: str
