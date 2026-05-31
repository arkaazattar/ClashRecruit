"""API helpers for recruiter workflows and clan listing metadata."""

from ..clash_http_client import get as clash_get


def extract_clan_requirements(payload: object) -> list[int]:
    """Extract clan requirements from a Clash clan detail payload."""
    if not isinstance(payload, dict):
        return [0, 0, 0]

    required_league = 0
    required_builder_trophies = payload.get("requiredBuilderBaseTrophies") or 0
    required_townhall = payload.get("requiredTownhallLevel") or 0
    return [required_league, required_builder_trophies, required_townhall]


class Recruiter:
    """Wrap Clash API calls used by recruiter-facing routes."""

    def __init__(self, clan_tag: str | None, headers: dict[str, str]) -> None:
        """Initialize recruiter API context for a clan.

        Args:
            clan_tag (str | None): Clan tag used for clan API lookups.
            headers (dict[str, str]): HTTP headers for Clash API requests.
        """
        self.headers = headers
        self.clan_tag = clan_tag
        self.requirements: list[int | None] = []

    def pull_clan_requirements(self) -> list[int | None]:
        """Fetch and store current clan join requirements.

        Returns:
            list: Clan requirements in order `[league, builder, townhall]`.
        """
        response = clash_get(
            f"https://api.clashofclans.com/v1/clans/%23{self.clan_tag}",
            headers=self.headers,
        )
        self.storage = response.payload
        self.new_clan_requirements(*extract_clan_requirements(self.storage))

        return self.requirements

    def lookup_clan(self, request: str | None = None) -> dict[str, object]:
        """Fetch clan metadata from the Clash API.

        Args:
            request (str | None, optional): Optional narrowed payload mode.
                Supported values are ``"member_count"`` and
                ``"description"``.

        Returns:
            dict: Clan metadata payload for the selected request mode.
        """
        response = clash_get(
            f"https://api.clashofclans.com/v1/clans/%23{self.clan_tag}",
            headers=self.headers,
        )
        response = response.payload
        rsp: dict[str, object] = {}

        if request is None:
            rsp["name"] = response.get("name")
            rsp["type"] = response.get("type")
            rsp["description"] = response.get("description")
            rsp["location"] = {
                "id": response.get("location", {}).get("id"),
                "name": response.get("location", {}).get("name"),
            }
            rsp["badge"] = response.get("badgeUrls").get("medium")
            rsp["clan_level"] = response.get("clanLevel")
            rsp["member_count"] = response.get("members")
            rsp["warFrequency"] = response.get("warFrequency")
            rsp["clanPoints"] = response.get("clanPoints")

        elif request == "member_count":
            rsp["member_count"] = response.get("members")

        elif request == "description":
            rsp["description"] = response.get("description")

        return rsp

    def new_clan_requirements(
        self,
        required_league: int | None,
        required_builder_trophies: int | None,
        required_townhall: int | None,
    ) -> None:
        """Set all clan requirements and store them in canonical list order."""
        self.required_league = required_league
        self.required_builder_trophies = required_builder_trophies
        self.required_townhall = required_townhall
        self.requirements = [
            self.required_league,
            self.required_builder_trophies,
            self.required_townhall,
        ]
