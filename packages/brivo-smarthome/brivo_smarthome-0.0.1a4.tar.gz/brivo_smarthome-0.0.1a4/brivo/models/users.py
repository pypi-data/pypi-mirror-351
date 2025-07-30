from datetime import datetime
from enum import IntEnum
from random import randint
from typing import Literal, Any

from pydantic import Field, field_serializer

from brivo.models.base import BaseBrivoModel, ResourceLink, BrivoDateTime
from brivo.models.company import RegisteredCompany, RegisteredCompanySummary
from brivo.models.unit import Unit


class UserRole(IntEnum):
    SUPER_ADMIN = 1
    TECHNICIAN = 2
    ADMIN = 3
    GUEST_MANAGER = 4
    OWNER = 5
    STAFF = 6
    GUEST = 7
    VENDOR = 8
    INSTALLER = 9

    @property
    def name(self):
        return {
            UserRole.SUPER_ADMIN: "Super Admin",
            UserRole.TECHNICIAN: "Technician",
            UserRole.ADMIN: "Admin",
            UserRole.GUEST_MANAGER: "Guest Manager",
            UserRole.OWNER: "Owner",
            UserRole.STAFF: "Staff",
            UserRole.GUEST: "Guest",
            UserRole.VENDOR: "Vendor",
            UserRole.INSTALLER: "Installer",
        }[self]

class UserSummaryV3(BaseBrivoModel):
    id: int
    first_name: str
    last_name: str
    alternate_id: str | None
    email: str | None
    role: UserRole = Field(validation_alias='group', serialization_alias='group')
    is_overridden: bool
    start_time: BrivoDateTime
    end_time: BrivoDateTime | None
    phone: str | None
    type: Literal['access_window', 'anytime']
    status: str  # Literal['removed', ...]
    access_type: Literal['company', 'property', 'multi_property'] | None = None
    temp_disabled: bool
    has_schedule: bool | dict

class User(BaseBrivoModel):
    code: str | None = Field(default_factory=lambda: User._generate_random_code())
    companies: list[RegisteredCompanySummary] | None = Field(None, validation_alias='company', serialization_alias='company')
    delivery_method: Literal['none', 'email', 'sms', 'email_sms'] = 'none'
    email: str | None = None
    end_time: BrivoDateTime | None = None
    first_name: str
    is_code: bool = True
    is_locking: bool = True
    last_name: str
    mobile_pass: str | None = Field(None, frozen=True) # Unknown type. guessing it's a string.
    phone: str | None = None
    role: UserRole = Field(UserRole.GUEST, validation_alias='group', serialization_alias='group')
    start_time: BrivoDateTime = Field(default_factory=datetime.now)
    temp_disabled: bool = False
    type: Literal['Access']
    units: list[Unit] | None = Field(None, validation_alias='property', serialization_alias='property')

    @field_serializer('companies')
    def serialize_companies(self, companies: list[RegisteredCompany]):
        return [company.id for company in companies] if companies else None

    @field_serializer('units')
    def serialize_units(self, units: list[Unit]):
        return [unit.id for unit in units] if units else None

    @staticmethod
    def _generate_random_code() -> str:
        return format(randint(0, 9999), '04')

    def randomize_code(self):
        self.code = self._generate_random_code()

class RegisteredUser(User):
    id: int = Field(frozen=True)
    access_trailing_key: str | None = Field(frozen=True)
    alternate_id: str | None = Field(None, frozen=True)
    emergency_state: Literal['not', 'used'] = Field('not', frozen=True)
    has_schedule: bool = False
    is_overridden: bool = False
    type: Literal['access_window', 'anytime']


class Profile(BaseBrivoModel):
    id: int = Field(frozen=True)
    email: str
    first_name: str
    last_name: str
    bio: str | None = None
    phone: str = ''
    is_active: bool
    is_superuser: bool
    role: UserRole = Field(validation_alias='group', serialization_alias='group')
    last_viewed_company: int
    system_message: bool
    password_last_changed: BrivoDateTime

class AccessV3(BaseBrivoModel):
    id: int
    data_relationship: Literal['property', 'company']
    alternate_id: str | None
    code: Any  # Unknown type
    delivery_method: Literal['none', 'email', 'sms', 'email_sms']
    email: str | None = None
    start_time: BrivoDateTime
    end_time: BrivoDateTime | None
    first_name: str
    last_name: str
    group: UserRole
    is_code: bool
    is_locking: bool
    is_overridden: bool
    phone: str | None
    type: Literal['access_window', 'anytime']
    access_trailing_key: str | None
    links: ResourceLink