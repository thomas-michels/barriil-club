from typing import Union
from requests import post, put, get, delete, patch


class HTTPClient:

    def __init__(self, headers: dict) -> None:
        self.headers = headers

    def post(self, url: str, data: dict = None, params: dict = None) -> Union[int, dict]:

        response = post(
            url=url,
            headers=self.headers,
            params=params,
            data=data
        )

        if response.status_code != 204:
            return response.status_code, response.json()

        return 204, None

    def patch(self, url: str, data: dict = None, params: dict = None) -> Union[int, dict]:

        response = patch(
            url=url,
            headers=self.headers,
            params=params,
            json=data
        )

        return response.status_code, response.json()

    def put(self, url: str, data: dict = None, params: dict = None) -> Union[int, dict]:

        response = put(
            url=url,
            headers=self.headers,
            params=params,
            json=data
        )

        return response.status_code, response.json()

    def get(self, url: str, params: dict = None, raw: bool = False) -> Union[int, dict]:

        response = get(
            url=url,
            headers=self.headers,
            params=params
        )

        if response.status_code != 204:
            if raw:
                return response

            return response.status_code, response.json()

        return 204, None

    def delete(self, url: str, data: dict = None, params: dict = None) -> Union[int, dict]:

        response = delete(
            url=url,
            headers=self.headers,
            params=params,
            json=data
        )

        if response.status_code != 204:
            return response.status_code, response.json()

        return 204, None
