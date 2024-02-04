from pydantic_settings import BaseSettings


class GlobalСonfig(BaseSettings):
    DEBUG_MODE: bool = True


global_config = GlobalСonfig()
