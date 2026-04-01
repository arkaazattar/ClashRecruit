"""Core Clash API wrapper for player validation and profile lookups."""

from typing import Literal

import requests

REQUESTOPTIONS = Literal[
    "expLevel",
    "leagueTier",
    "builderBaseLeague",
    "builderHallLevel",
    "clan"
]


class API:
    """Represent a player session backed by Clash API data."""

    def __init__(
        self,
        user_tag: str,
        api: str | None,
        headers: dict[str, str],
    ) -> None:
        """Initialize API session state for a player.

        Args:
            user_tag (str): Player tag for the current session.
            api (str | None): Optional player API token for verification.
            headers (dict[str, str]): HTTP headers for Clash API requests.
        """
        self.headers = headers
        self.token = False
        self.user_tag = user_tag
        self.user_name = "Guest"
        self.json_data = {
            "token": api
        }
        self.clantag = ""
        self.recruiter_status = ""
        self.league = 0
        self.builder_trophies = 0
        self.townhall = 0
        self.townhallWeaponLevel = None

    def check_player_api(self) -> bool:
        """Validate the provided player API token with Clash verification API.

        Returns:
            bool: ``True`` when the token is valid, otherwise ``False``.
        """
        url = (
            "https://api.clashofclans.com/v1/players/"
            f"%23{self.user_tag}/verifytoken"
        )

        response = requests.post(
            url,
            headers=self.headers,
            json=self.json_data,
        )
        self.apistorage = response.json()

        status = self.apistorage.get("status")

        if status == "ok":
            self.token = True

        elif status == "invalid":
            self.reason = "API Token is incorrect"

        else: self.reason = self.apistorage
        return self.token

    def check_player(
        self,
        request: list[REQUESTOPTIONS] | None = None,
    ) -> bool | dict[str, object]:
        """Validate and load player data for session use.

        Args:
            request (list[REQUESTOPTIONS] | None, optional): Optional subset
                of player fields to return instead of a boolean.

        Returns:
            bool | dict: ``True`` for successful validation,
                ``False`` for invalid user/token states, or a filtered player
                response dictionary when ``request`` is provided.
        """
        if self.user_tag == "Guest":
            self.reason = "User is a Guest"
            return False
        url = f"https://api.clashofclans.com/v1/players/%23{self.user_tag}"
        response = requests.get(url, headers=self.headers)
        self.storage = response.json()
        reason = self.storage.get("reason")

        if reason == "notFound":
            self.reason = "Player tag is incorrect"
            return False

        if reason == "accessDenied.invalidIp":
             self.reason = "Invalid IP"
             return False

        if self.json_data["token"] and self.check_player_api() == False:
            return False

        self.league = self.storage.get("leagueTier").get("name")
        if self.league != 'Unranked':
            self.league = int(self.league[-2:])
        else: self.league = 0
        self.townhall = self.storage.get("townHallLevel")
        self.builder_trophies = self.storage.get("builderBaseTrophies")

        if self.townhall <= 17:
            self.townhallWeaponLevel = self.storage.get("townHallWeaponLevel")

        self.recruiter_status = self.recruiting(self.storage)
        self.clantag = self.storage.get("clan", {}).get("tag", None)
        if self.clantag:
            self.clantag = self.clantag[1:]
        self.user_name = self.storage.get("name")

        if request:
            response = {
                "player_tag": self.user_tag
            }

            for request_key in request:
                response[request_key] = self.storage.get(request_key, None)

            if response.get("clan", None):
                response["clan"]["role"] = self.storage.get("role")
                response["num_items"] = 6
            else:
                response["num_items"] = 5

            return response

        return True

    def recruiting(self, data: dict[str, object]) -> bool:
        """Return whether a player can recruit based on clan role membership.

        Args:
            data (dict): Player payload that includes clan and role fields.

        Returns:
            bool: ``True`` for leader/coleader/admin clan roles,
                else ``False``.
        """
        roles = ["leader", "coleader", "admin"]

        clan_tag = data.get("clan", {}).get("tag", 0)
        if(clan_tag == 0):
            return False

        if(data["role"].lower() not in roles):
            return False

        return True
