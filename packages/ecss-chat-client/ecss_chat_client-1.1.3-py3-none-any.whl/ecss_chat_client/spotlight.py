from requests import Response

from .lib import Base


class Spotlight(Base):
    """Сервис Spotlight."""

    def search_by_spotlight(self, page_count: int, search_query: str,
                            search_schema: list) -> Response:
        """Поиск в Spotlight по определенной схеме."""
        return self._make_request(
            'spotlight',
            payload={
                'count': page_count,
                'query': search_query,
                'searchSchema': search_schema
            }
        )
