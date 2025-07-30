from pydantic import BaseModel
from typing import Dict

from ..enums import HttpMethod


class ExchangeApiRequest(BaseModel):
    url: str
    method: HttpMethod
    params: dict[str, str | int] = {}
    body: dict[str | int, str | Dict] = {}
    body_params_list: list = []
    headers: dict[str, str] = {}
    execute_at: int | None = None

    # Для ордеров по расписанию:
    # TODO: Добавить поле тип запроса, e.g. 'PLACE_ORDER', 'CANCEL_ORDER'
    # TODO: Добавить поле user_id - чтобы различать, от имени какого пользователя будет ордер
    # TODO: Добавить поле exhcange_account_id - чтобы различать, на какой аккаунт будет ордер

    # class Config:
    #     use_enum_values = True


