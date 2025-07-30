from datetime import datetime
from typing import Any

from brivo_smarthome.models.base import BaseBrivoModel, BrivoDateTime


class RegisteredUnitSummary(BaseBrivoModel):
    id: int
    name: str
    description: str
    address_1: str
    address_2: str | None
    zipcode: str
    city: str
    state: str
    master_code: str
    created_at: BrivoDateTime
    updated_at: BrivoDateTime
    temp: int | None
    secure: bool | None
    dry: bool | None
    is_active: bool
    user: int
    company: int
    trailing_key: str | None


class Unit(BaseBrivoModel):
    id: int
    name: str
    description: str
    address_1: str
    address_2: str | None
    zipcode: str
    city: str
    state: str
    master_code: str
    created_at: datetime
    updated_at: datetime
    temp: int
    secure: bool
    dry: bool | None
    is_active: bool
    user: int
    co: bool
    smoke: bool
    timezone: str | None
    parent_timezone: str | None

class UnitSummaryV3(BaseBrivoModel):
    id: int
    name: str
    address_1: str
    address_2: str | None
    zipcode: str
    city: str
    state: str
    is_automated: bool
    ordering: str
    is_occupied: bool
    is_demo: bool
    is_home: bool
    country: str
    renters: str
    has_children: int
    alerts: list[Any]  # Unknown type
    timezone: str | None