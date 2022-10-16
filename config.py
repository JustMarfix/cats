# GNU AFFERO GENERAL PUBLIC LICENSE

from dataclasses import dataclass


@dataclass()
class Config:
    # tg
    token: str = "Токен от бота Telegram"
    admin_id: int = 1111111111 # Ваш циферный Telegram ID, или ID чата

    # database
    user: str = "Логин от сервера с MariaDB"
    password: str = "Пароль от сервера с MariaDB"
    database: str = "Название БД"
    host: str = "Домен/IP сервера MariaDB"
    port: int = 3306 # Это стандартный порт MariaDB, но вы можете его изменить

    # cats
    url: str = "https://api.thecatapi.com/v1/images/search?limit=1&token=<ваш токен от TheCatAPI>"
