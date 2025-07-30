from typing import Generator, Any, Iterable

import httpx

from brivo.models.unit import UnitSummaryV3
from brivo.models.users import User, RegisteredUser, Profile, UserSummaryV3


class BrivoRequests:

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')

    def _request(self, method: str, endpoint: str, payload: dict = None, params: dict[str, Any] = None) -> httpx.Request:
        params = {k: v for k, v in params.items() if v is not None} if params else {}
        return httpx.Request(method, f'{self.base_url}{endpoint}', json=payload, params=params)

    def get(self, endpoint: str, params: dict[str, Any] = None) -> httpx.Request:
        return self._request('GET', endpoint, params=params)

    def patch(self, endpoint: str, payload: dict = None) -> httpx.Request:
        return self._request('PATCH', endpoint, payload=payload)

    def post(self, endpoint: str, payload: dict = None) -> httpx.Request:
        return self._request('POST', endpoint, payload=payload)

    def put(self, endpoint: str, payload: dict = None) -> httpx.Request:
        return self._request('PUT', endpoint, payload=payload)

    def delete(self, endpoint: str, payload: dict) -> httpx.Request:
        return self._request('DELETE', endpoint)

    def company(self, company_id: int) -> httpx.Request:
        return self.get(f'/v3/company/{company_id}')

    def company_accesses(self, company_access_id: int) -> httpx.Request:
        return self.get(f'/v3/company/access/{company_access_id}')

    def company_users(self, company_id: int) -> Generator[Iterable[httpx.Request], Iterable[httpx.Response], None]:
        # return self.get(f'/v1/companies/{company_id}/accesses')  # This endpoint is slow AF. Workaround ...
        units = []
        responses = yield [self.units(company_id)] # UnitSummaryV3
        for response in responses:
            results = response.json()['results'] if 'results' in response.json() else []
            units.extend(UnitSummaryV3.model_validate(result) for result in results)
        requests = [self.unit_users(unit.id) for unit in units]
        yield requests

    def units(self, company_id: int, page: int = 1, view: str = 'dashboard', unit_id = None) -> httpx.Request:
        params = {
            'company': company_id,
            'page': page,
            'parent': unit_id,
            'view': view
        }
        return self.get(f'/v3/property', params=params)

    def create_user(self, access: User) -> httpx.Request:
        if type(access) is not User:
            raise TypeError(f'Expected Access, got {type(access)}')
        return self.post('/v1/accesses', access.model_dump(exclude_none=True))

    def my_profile(self) -> httpx.Request:
        return self.get('/v1/users/me')

    def unit_accesses(self, property_access_id: int) -> httpx.Request:
        return self.get(f'/v3/property/access/{property_access_id}')

    def unit_users(self, unit_id: int) -> httpx.Request:
        return self.get(f'/v3/property/{unit_id}/accesses')

    def my_v3_accesses(self) -> httpx.Request:
        return self.get('/v3/user/access')

    def update_user(self, access: RegisteredUser) -> httpx.Request:
        endpoint = f'/v1/accesses/{access.id}'
        return self.patch(endpoint, access.model_dump(exclude_none=True))

    def update_profile(self, profile: Profile) -> httpx.Request:
        return self.put('/v1/users/me', profile.model_dump(exclude_none=True))

    def user(self, user_id):
        return self.get(f'/v1/accesses/{user_id}')