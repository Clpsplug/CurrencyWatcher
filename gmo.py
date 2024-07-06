from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, get_type_hints, List, get_args, get_origin

import requests
from dataclass_wizard import JSONWizard
from dataclass_wizard.errors import ParseError


@dataclass
class GMOData(JSONWizard):
    pass


@dataclass
class GMOResponse:
    status: int
    data: GMOData
    responsetime: str

    @classmethod
    def create(cls, d: dict):
        parsed = cls(**d)
        # 'data' will be parsed as dict, which is not ideal. We'll convert it to data class.
        data_info = get_type_hints(cls).get('data', GMOData)
        try:
            parsed.data = data_info.from_dict(d['data'])
        except (AttributeError, ParseError):
            # In this case, the data might be list.
            list_item_info = parsed.__annotations__['data']
            if get_origin(list_item_info) is not list:
                raise Exception(f"Data is not list or dict. It's actually {list_item_info}.")
            parsed.data = get_args(list_item_info)[0].from_list(d['data'])

        return parsed

    def get_response_time(self) -> datetime:
        parsed_time = datetime.strptime(self.responsetime, "%Y-%m-%dT%H:%M:%S.%fZ")
        return parsed_time

    def get_readable_time(self) -> str:
        return self.get_response_time().strftime("%Y/%m/%d %H:%M:%S")


class GMOAPIBase(ABC):
    def __init__(self):
        self.endpoint = 'https://forex-api.coin.z.com/public'
        self.path: str

    @abstractmethod
    def call(self) -> GMOResponse:
        pass


@dataclass
class Status(GMOData):
    status: Literal["MAINTENANCE", "CLOSE", "OPEN"]


@dataclass
class StatusResponse(GMOResponse):
    data: Status


class GMOStatus(GMOAPIBase):

    def __init__(self):
        super().__init__()
        self.path = '/v1/status'

    def call(self) -> StatusResponse:
        response = requests.get(self.endpoint + self.path)

        return StatusResponse.create(response.json())


@dataclass
class CurrencyData(GMOData):
    ask: float
    bid: float
    symbol: str
    timestamp: str
    status: Literal["CLOSE", "OPEN"]


@dataclass
class CurrencyResponse(GMOResponse):
    data: List[CurrencyData]


class GMOCurrency(GMOAPIBase):
    def __init__(self):
        super().__init__()
        self.path = '/v1/ticker'

    def call(self) -> CurrencyResponse:
        response = requests.get(self.endpoint + self.path)

        return CurrencyResponse.create(response.json())
