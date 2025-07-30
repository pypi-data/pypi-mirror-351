from asyncio import gather
from typing import Iterable

import httpx

from brivo import App
from brivo.models.company import RegisteredCompany, RegisteredCompanySummary
from brivo.models.unit import RegisteredUnitSummary
from brivo.models.users import User, RegisteredUser, Profile, UserSummaryV3, AccessV3


class AsyncApp(App):
    def __init__(self, username: str = None, password: str = None, base_url: str = None, company_id: int | None = None):
        super().__init__(username, password, base_url, company_id)
        self.client = httpx.AsyncClient(auth=self.auth, base_url=self.base_url)

    async def _handle_request(self, request: httpx.Request, read: bool = True) -> httpx.Response:
        response = await self.client.send(request)
        response.raise_for_status()
        if read:
            await response.aread()
        return response

    async def _handle_requests(self, requests: Iterable[httpx.Request], read: bool = True) -> list[httpx.Response]:
        responses = await gather(*[self.client.send(request) for request in requests])
        if read:
            await gather(*[response.aread() for response in responses])
        return responses

    async def _fetch_accesses(self) -> tuple[list[RegisteredCompanySummary], list[RegisteredUnitSummary]]:
        v3_accesses = await self.my_v3_accesses()
        company_access_ids = [access.id for access in v3_accesses if access.data_relationship == 'company']
        unit_access_ids = [access.id for access in v3_accesses if access.data_relationship == 'property']

        company_tasks = [self.company_accesses_by_id(company_id) for company_id in company_access_ids]
        unit_tasks = [self.unit_accesses_by_id(unit_id) for unit_id in unit_access_ids]
        all_results = await gather(*(company_tasks + unit_tasks))

        companies_accesses = []
        unit_accesses = []

        # First part of results are company accesses
        for i in range(len(company_tasks)):
            companies_accesses.extend(all_results[i])
        # Remaining results are unit accesses
        for i in range(len(company_tasks), len(all_results)):
            unit_accesses.extend(all_results[i])
        return companies_accesses, unit_accesses

    async def company(self, company_id: int) -> RegisteredCompany:
        response = await self._handle_request(self._requests.company(company_id))
        return RegisteredCompany.model_validate(response.json())

    async def company_accesses_by_id(self, company_access_id: int) -> list[RegisteredCompanySummary]:
        response = await self._handle_request(self._requests.company_accesses(company_access_id))
        return [RegisteredCompanySummary.model_validate(access) for access in response.json()]

    async def company_users(self, company_id: int) -> list[UserSummaryV3]:
        factory = self._requests.company_users(company_id)
        responses = []
        try:
            requests = next(factory)
            while True:
                responses = await self._handle_requests(requests)
                requests = factory.send(responses)
        except StopIteration:
            users = []
            for response in responses:
                results = response.json()['company'] if 'company' in response.json() else []
                users.extend(UserSummaryV3.model_validate(result) for result in results if result['id'] not in {user.id for user in users})
            return users

    async def create_access(self, access: User) -> RegisteredUser:
        response = await self._handle_request(self._requests.create_user(access))
        return RegisteredUser.model_validate(response.json())

    async def my_company_ids(self) -> list[int]:
        companies_accesses, unit_accesses = await self._fetch_accesses()

        my_companies = set()
        for company in companies_accesses:
            my_companies.add(company.id)
        for unit in unit_accesses:
            my_companies.add(unit.company)
        return list(my_companies)

    async def my_profile(self) -> Profile:
        response = await self._handle_request(self._requests.my_profile())
        return Profile.model_validate(response.json())

    # async def my_accesses(self) -> dict:
    #     return (await self._handle_request(self._requests.my_accesses())).json()

    async def my_v3_accesses(self) -> list[AccessV3]:
        response = await self._handle_request(self._requests.my_v3_accesses())
        accesses = response.json()
        return [AccessV3.model_validate(access) for access in accesses['results'] if 'results' in accesses]

    async def unit_accesses_by_id(self, property_access_id: int) -> list[RegisteredUnitSummary]:
        response = await self._handle_request(self._requests.unit_accesses(property_access_id))
        return [RegisteredUnitSummary.model_validate(access) for access in response.json()]

    async def update_access(self, access: RegisteredUser) -> RegisteredUser:
        response = await self._handle_request(self._requests.update_user(access))
        return RegisteredUser.model_validate(response.json())

    async def update_profile(self, profile: Profile) -> Profile:
        response = await self._handle_request(self._requests.update_profile(profile))
        return profile.update_from_response(response.json())

    async def update_user(self, user: RegisteredUser) -> None:
        await self._handle_request(self._requests.update_user(user))

    async def user(self, user_id: int) -> RegisteredUser:
        response = await self._handle_request(self._requests.user(user_id))
        return RegisteredUser.model_validate(response.json())
