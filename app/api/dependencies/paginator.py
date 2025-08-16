from math import ceil
from starlette.requests import Request
import re
from app.api.exceptions.paginator import InvalidPageAccess


_PAGE_REGEX = re.compile(r"page=\d+")


class Paginator:
    def __init__(self, request: Request, pagination: dict):
        self._request = request

        page = int(pagination.get("page", 1))
        page_size = int(pagination.get("page_size", 10))

        self._page = page
        self._page_size = page_size

        self.offset = int(page * page_size - page_size)

    def set_total(self, total: int):
        self._total = total
        self._pages = ceil(self._total / self._page_size)

        if self._pages < self._page and self._page > 1:
            raise InvalidPageAccess("Invalid Page Access")

    @property
    def page_size(self):
        return self._page_size

    @property
    def pagination(self):
        url = self._request.url.path
        query = self._request.url.query
        if self._page < self._pages:
            next_page = f"page={self._page + 1}"
            query_params = _PAGE_REGEX.sub(next_page, query)
            next_url = f"{url}?{query_params}"
        else:
            next_url = None

        if self._page > 1:
            previous_page = f"page={self._page - 1}"
            query_params = _PAGE_REGEX.sub(previous_page, query)
            previous_url = f"{url}?{query_params}"

        else:
            previous_url = None

        return {
            "total": self._total,
            "page_size": self._page_size,
            "pages": self._pages,
            "page": self._page,
            "links": {
                "previous": previous_url,
                "next": next_url,
                "self": f"{url}?{query}"
            },
        }
