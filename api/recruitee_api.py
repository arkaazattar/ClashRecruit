"""API helpers for recruitee-facing clan search requests."""

from ..clash_http_client import ClashApiHTTPError
from ..clash_http_client import get as clash_get


class Recruitee:
    """Wrap Clash API calls used by recruitee search routes."""

    def __init__(self, user_tag: str | None, headers: dict[str, str]) -> None:
        """Initialize recruitee API context for clan search calls.

        Args:
            user_tag (str | None): Player tag for the current user.
            headers (dict[str, str]): HTTP headers for Clash API requests.
        """
        self.headers = headers
        self.user_tag = user_tag

    def searchClan(
        self,
        filter: dict[str, object],
        after: str | None = None,
    ) -> dict[str, object]:
        """Search clans using provided filters and optional pagination cursor.

        Args:
            filter (dict): Query filters forwarded to the Clash clan endpoint.
            after (str | None, optional): Pagination cursor for the next page.

        Returns:
            dict: Response payload containing ``items``, ``after``, and
                optional ``error`` metadata.
        """
        url = "https://api.clashofclans.com/v1/clans"
        if after:
            filter["after"] = after

        error = None
        try:
            response = clash_get(url, params=filter, headers=self.headers)
            storage = response.payload
        except ClashApiHTTPError as exc:
            storage = exc.payload
            error = {
                "reason": storage.get("reason"),
                "message": storage.get("message"),
                "status": exc.status_code,
            }

        return {
            "items": storage.get("items", []),
            "after": storage.get("paging", {}).get("cursors", {}).get("after"),
            "error": error,
        }
