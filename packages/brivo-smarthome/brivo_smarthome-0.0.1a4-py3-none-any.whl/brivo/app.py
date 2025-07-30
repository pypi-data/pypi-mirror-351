from typing import Iterable

import httpx

from brivo.base_app import BaseBrivoClient
from brivo.models.company import RegisteredCompany, RegisteredCompanySummary
from brivo.models.unit import RegisteredUnitSummary, UnitSummaryV3
from brivo.models.users import User, RegisteredUser, Profile, AccessV3, UserSummaryV3


class App(BaseBrivoClient):
    def __init__(self, username: str = None, password: str = None, base_url: str = None, company_id: int | None = None):
        super().__init__(username, password, base_url, company_id)
        self.client = httpx.Client(auth=self.auth, base_url=self.base_url, timeout=15)

    def _handle_request(self, request: httpx.Request, read: bool = True) -> httpx.Response:
        response = self.client.send(request)
        response.raise_for_status()
        if read:
            response.read()
        return response

    def _handle_requests(self, requests: Iterable[httpx.Request], read: bool = True) -> list[httpx.Response]:
        responses: list[httpx.Response] = []
        for request in requests:
            responses.append(self._handle_request(request, read))
        return responses

    def _fetch_accesses(self) -> tuple[list[RegisteredCompanySummary], list[RegisteredUnitSummary]]:
        v3_accesses = self.my_v3_accesses()
        unit_access_ids = [access.id for access in v3_accesses if access.data_relationship == 'property']
        company_access_ids = [access.id for access in v3_accesses if access.data_relationship == 'company']
        companies_accesses = []
        unit_accesses = []

        for company_access_id in company_access_ids:
            companies_accesses += self.company_accesses_by_id(company_access_id)
        for unit_access_id in unit_access_ids:
            unit_accesses += self.unit_accesses_by_id(unit_access_id)

        return companies_accesses, unit_accesses

    def company(self, company_id: int) -> RegisteredCompany:
        response = self._handle_request(self._requests.company(company_id))
        return RegisteredCompany.model_validate(response.json())

    def company_accesses_by_id(self, company_access_id: int) -> list[RegisteredCompanySummary]:
        response = self._handle_request(self._requests.company_accesses(company_access_id))
        return [RegisteredCompanySummary.model_validate(access) for access in response.json()]

    def unit_users(self, unit_id: int, include_company_users: bool = False) -> list[UserSummaryV3]:
        response = self._handle_request(self._requests.unit_users(unit_id))
        users = []
        if include_company_users:
            company_users = response.json()['company'] if 'company' in response.json() else []
            users.extend([UserSummaryV3.model_validate(user for user in company_users)])
        unit_users = response.json()['property'] if 'property' in response.json() else []
        users.extend([UserSummaryV3.model_validate(user) for user in unit_users])
        return users

    def units(self, company_id: int, unit_id: int = None) -> list[UnitSummaryV3]:
        response = self._handle_request(self._requests.units(company_id=company_id, unit_id=unit_id))
        units = response.json()['results'] if 'results' in response.json() else []
        return [UnitSummaryV3.model_validate(unit) for unit in units]

    def company_users(self, company_id: int) -> list[UserSummaryV3]:
        factory = self._requests.company_users(company_id)
        responses = []
        try:
            requests = next(factory)
            while True:
                responses = self._handle_requests(requests)
                requests = factory.send(responses)
        except StopIteration:
            users = []
            for response in responses:
                results = response.json()['company'] if 'company' in response.json() else []
                users.extend(UserSummaryV3.model_validate(result) for result in results if result['id'] not in {user.id for user in users})
            return users

    def create_user(self, access: User) -> RegisteredUser:
        response = self._handle_request(self._requests.create_user(access))
        return RegisteredUser.model_validate(response.json())

    def my_v3_accesses(self) -> list[AccessV3]:
        response = self._handle_request(self._requests.my_v3_accesses())
        accesses = response.json()
        return [AccessV3.model_validate(access) for access in accesses['results'] if 'results' in accesses]

    def my_company_ids(self) -> list[int]:
        companies_accesses, unit_accesses = self._fetch_accesses()

        my_companies = set()
        for company in companies_accesses:
            my_companies.add(company.id)
        for unit in unit_accesses:
            my_companies.add(unit.company)
        return list(my_companies)

    def my_unit_ids(self) -> list[int]:
        companies_accesses, unit_accesses = self._fetch_accesses()

        my_units = set()
        for company in companies_accesses:
            for unit in self.units(company.id):
                my_units.add(unit.id)
        for unit in unit_accesses:
            my_units.add(unit.id)
        return list(my_units)

    def my_profile(self) -> Profile:
        response = self._handle_request(self._requests.my_profile())
        return Profile.model_validate(response.json())

    def unit_accesses_by_id(self, property_access_id: int) -> list[RegisteredUnitSummary]:
        response = self._handle_request(self._requests.unit_accesses(property_access_id))
        return [RegisteredUnitSummary.model_validate(access) for access in response.json()]

    def update_user(self, user: RegisteredUser) -> None:
        response = self._handle_request(self._requests.update_user(user))

    def user(self, user_id: int) -> RegisteredUser:
        response = self._handle_request(self._requests.user(user_id))
        return RegisteredUser.model_validate(response.json())

    def update_profile(self, profile: Profile) -> Profile:
        req = self._requests.update_profile(profile)
        response = self._handle_request(req)
        return profile.update_from_response(response.json())