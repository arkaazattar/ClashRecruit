"""API helpers for recruiter workflows and clan listing metadata."""

import requests


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
        response = requests.get(
            f"https://api.clashofclans.com/v1/clans?name=%23{self.clan_tag}",
            headers=self.headers,
        )
        self.storage = response.json()
        long_list = self.storage.get("items") or []
        required_townhall = 0
        required_builder_trophies = 0
        required_league = 0
        for i in range(len(long_list)):
            required_townhall = long_list[i].get("requiredTownhallLevel")
            required_builder_trophies = long_list[i].get(
                "requiredBuilderBaseTrophies"
            )

        self.new_clan_requirements(
            required_league,
            required_builder_trophies,
            required_townhall,
        )

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
        response = requests.get(
            f"https://api.clashofclans.com/v1/clans/%23{self.clan_tag}",
            headers=self.headers,
        )
        response = response.json()
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
