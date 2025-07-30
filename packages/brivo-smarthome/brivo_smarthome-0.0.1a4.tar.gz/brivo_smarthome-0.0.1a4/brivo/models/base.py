from datetime import datetime, timezone
from typing import Self, Literal, Annotated

from pydantic import BaseModel, ConfigDict, PlainSerializer, PrivateAttr

BrivoDateTime = Annotated[
    datetime,
    PlainSerializer(lambda x: x.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z', return_type=str),
]

class BaseBrivoModel(BaseModel):
    model_config = ConfigDict(extra='allow', serialize_by_alias=True, validate_by_alias=True)

    def update_from_response(self, response_object: Self) -> Self:
        for attr, value in self.__dict__.items():
            if hasattr(response_object, attr):
                setattr(self, attr, getattr(response_object, attr))
        return self

class ResourceLink(BaseBrivoModel):
    href: str
    rel: str
    type: Literal['GET', 'PATCH', 'POST', 'PUT', 'DELETE']
