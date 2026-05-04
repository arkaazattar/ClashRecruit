"""API helpers for recruitee-facing clan search requests."""

import requests


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

        response = requests.get(url, params=filter, headers=self.headers)

        storage = response.json()

        error = None
        if response.status_code >= 400:
            error = {
                "reason": storage.get("reason"),
                "message": storage.get("message"),
                "status": response.status_code,
            }

        return {
            "items": storage.get("items", []),
            "after": storage.get("paging", {}).get("cursors", {}).get("after"),
            "error": error,
        }
