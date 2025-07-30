from typing import Annotated, Any

from pydantic import Field

from brivo.models.base import BaseBrivoModel

class RegisteredCompanySummary(BaseBrivoModel):
    id: int
    name: str
    img: str  # URL to the company logo
    address_1: str
    address_2: str | None
    zipcode: str
    city: str
    state: str
    trailing_key: str | None = None

class RegisteredCompany(RegisteredCompanySummary):
    model_config = BaseBrivoModel.model_config.copy()
    model_config.update(arbitrary_types_allowed=True)

    phone: str | None
    code_length: Annotated[int, Field(ge=4, le=6)]
    email_send_day: Any | None # Unknown type
    timezone: str
    group: int
    type: str
    sync_start: str
    sync_remove: str
    has_messaging: bool
    after_hours_start: str
    after_hours_end: str
    country: str
    notification_type: str
    use_phone_as_usercode: bool
    code_capacity_alert_at: int
    access_denial_groups: list[Any] | None  # Unknown type
    scheduled_lock: Any | None  # Unknown type
    close_only_unoccupied: Any | None  # Unknown type
    trailing_key_enabled: bool
    data: dict