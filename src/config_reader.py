from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Setting(BaseSettings):
    """
    A class used to manage application settings.

    ...

    Attributes
    ----------
    pay_address : SecretStr
        The payment address.
    db_cluster_name : SecretStr
        The name of the database cluster.
    database : SecretStr
        The database.
    app_port : SecretStr
        The application port.

    Methods
    -------
    None
    """
    pay_address: SecretStr
    db_cluster_name: SecretStr
    database: SecretStr
    app_port: SecretStr

    class Config:
        env_file = '.env'
        env_encode = 'utf-8'


config = Setting()


