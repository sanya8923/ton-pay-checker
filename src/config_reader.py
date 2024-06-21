from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Setting(BaseSettings):
    pay_address: SecretStr
    db_cluster_name: SecretStr
    database: SecretStr
    app_port: SecretStr

    class Config:
        env_file = '.env'
        env_encode = 'utf-8'


config = Setting()


