from dataclasses import dataclass
from datetime import datetime, timezone
from typing import get_type_hints, get_origin, get_args, Literal, Annotated, Any

from dataclass_wizard import JSONWizard
from dataclass_wizard.errors import ParseError


@dataclass
class GMOData(JSONWizard):
    """Base data class for API response.
    This is meant to be a type for 'data' key within the JSON object returned by the API.
    """
    pass


@dataclass
class GMOResponse:
    """Base class for all API responses.

    Other API responses SHOULD inherit from this class.
    """
    status: Annotated[int, "Result of the API call. Only documented value is 0, which indicates success."]
    data: Annotated[GMOData, "Response of the API - the concrete type depends on the API called"]
    responsetime: Annotated[
        str, "String-encoded time of response, possibly in UTC. The format is in %Y-%m-%dT%H:%M:%S.%fZ."
    ]

    @classmethod
    def create(cls, d: dict[str, Any]) -> 'GMOResponse':
        """Parses the JSON dict response and returns a GMOResponse object.

        :param d: Dictionary object parsed from JSON response.
        :return: Marked as GMOResponse, but the inheriting class CAN assume itself as a return type.
        """
        parsed = cls(**d)
        # 'data' will be parsed as primitive dict or list, which is not ideal.
        # We'll convert it to the corresponding data class.
        data_info = get_type_hints(cls).get('data', GMOData)
        try:
            # Most of the time, the data is dict.
            parsed.data = data_info.from_dict(d['data'])
        except (AttributeError, ParseError):
            # FIXME: A bit ugly way to deal with data being either dict or list.
            # In this case, the data might be list.
            list_item_info = parsed.__annotations__['data']
            if get_origin(list_item_info) is not list:
                raise Exception(f"Data is not list or dict. It's actually {list_item_info}.")
            parsed.data = get_args(list_item_info)[0].from_list(d['data'])

        return parsed

    def get_response_time(self) -> datetime:
        # Returned time seems to be UTC
        parsed_time = datetime.strptime(self.responsetime, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
        # Pass None for local time (as in local time in which the machine runs)
        return parsed_time.astimezone(tz=None)

    def get_readable_time(self) -> str:
        return self.get_response_time().strftime("%Y/%m/%d %H:%M:%S")


@dataclass
class Status(GMOData):
    status: Literal["MAINTENANCE", "CLOSE", "OPEN"]


@dataclass
class StatusResponse(GMOResponse):
    """Market status response
    If data is 'MAINTENANCE', the app SHOULD postpone the next API attempt.
    """
    data: Annotated[Status, "Is the market open, or is the API itself under maintenance?"]


@dataclass
class CurrencyData(GMOData):
    ask: Annotated[float, "'ASK' rate, which is the current buying rate"]
    bid: Annotated[float, "'BID' rate, which is the current selling rate"]
    symbol: Annotated[
        str, "What rate do this data represent? Noted by 2 3-letter currency codes concatenated by an underscore."
    ]
    timestamp: Annotated[str, "Timestamp of this currency rate, possibly in UTC."]
    status: Annotated[Literal["CLOSE", "OPEN"], "State of the market."]


@dataclass
class CurrencyResponse(GMOResponse):
    """Latest currency rate response
    Data contains list of currency rate, each of which has the 'symbol' field,
    which can be used to determine which currency rate to display.
    """
    data: list[CurrencyData]
