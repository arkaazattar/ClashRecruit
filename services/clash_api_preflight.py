"""Development preflight check for Clash API reachability."""

from ..clash_http_client import ClashApiHTTPError
from ..clash_http_client import get as clash_get
from ..config import headers


def run_clash_api_preflight(headers=headers) -> None:
    """Call a lightweight Clash endpoint and raise if the API rejects this IP.


    Args:
        headers (dict[str, str], optional): HTTP headers sent with the Clash of
            Clans API request. Defaults to the module-level ``headers``
            imported
            from ``config``.

    Raises:
        Exception: Raised when the Clash API responds with an HTTP error
            status.
    """
    try:
        clash_get(
            (
                "https://api.clashofclans.com/v1/locations/32000249/"
                "rankings/players?limit=1"
            ),
            headers=headers,
        )
    except ClashApiHTTPError as exc:
        raise Exception(f"HTTP {exc.status_code}: {exc.reason}") from exc

    return


if __name__ == "__main__":
    run_clash_api_preflight()
