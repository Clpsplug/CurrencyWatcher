"""This module contains an actual API calls.
"""

from abc import ABC, abstractmethod

import requests

from domain import CurrencyResponse, StatusResponse, GMOResponse


class GMOAPIBase(ABC):
    def __init__(self):
        self._endpoint = 'https://forex-api.coin.z.com/public'
        self.__path: str

    @abstractmethod
    def call(self) -> GMOResponse:
        """Initiate the API call"""
        pass


class GMOStatus(GMOAPIBase):
    """State of the API itself"""

    def __init__(self):
        super().__init__()
        self.__path = '/v1/status'

    def call(self) -> StatusResponse:
        response = requests.get(self._endpoint + self.__path)

        return StatusResponse.create(response.json())


class GMOCurrency(GMOAPIBase):
    """Currency rates"""

    def __init__(self):
        super().__init__()
        self.__path = '/v1/ticker'

    def call(self) -> CurrencyResponse:
        response = requests.get(self._endpoint + self.__path)

        return CurrencyResponse.create(response.json())
