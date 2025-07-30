from typing import Optional, Dict, Any, Literal
from bwpfetcher.client import VoxylAPI
from bwpfetcher.endpoints import VoxylApiEndpoint
from bwpfetcher.exceptions import VoxylAPIError

api = VoxylAPI()

class Player:
    """
    Represents a Voxyl player, providing access to various player-related data 
    such as login info, stats, guild info, and rankings.
    """

    def __init__(self, uuid: str):
        """
        Initializes the Player with a UUID.
        
        Args:
            uuid (str): The UUID of the player.
        """
        self.uuid = uuid

    async def _fetch_info(self) -> Optional[Dict[str, Any]]:
        """
        Fetches player info from the PLAYER_INFO endpoint.

        Returns:
            Optional[Dict[str, Any]]: Player info data or None if the fetch fails.
        """
        try:
            return await api.fetch(VoxylApiEndpoint.PLAYER_INFO, uuid=self.uuid)
        except VoxylAPIError:
            return None

    async def _fetch_overall(self) -> Optional[Dict[str, Any]]:
        """
        Fetches overall player data such as level, XP, and wins.

        Returns:
            Optional[Dict[str, Any]]: Player overall data or None if the fetch fails.
        """
        try:
            return await api.fetch(VoxylApiEndpoint.PLAYER_OVERALL, uuid=self.uuid)
        except VoxylAPIError:
            return None

    async def _fetch_game(self) -> Optional[Dict[str, Any]]:
        """
        Fetches per-game player statistics.

        Returns:
            Optional[Dict[str, Any]]: Player game stats or None if the fetch fails.
        """
        try:
            return await api.fetch(VoxylApiEndpoint.PLAYER_GAME, uuid=self.uuid)
        except VoxylAPIError:
            return None

    async def _fetch_guild(self) -> Optional[Dict[str, Any]]:
        """
        Fetches guild-related player data.

        Returns:
            Optional[Dict[str, Any]]: Guild data or None if the fetch fails.
        """
        try:
            return await api.fetch(VoxylApiEndpoint.PLAYER_GUILD, uuid=self.uuid)
        except VoxylAPIError:
            return None

    @property
    async def last_login_time(self) -> Optional[int]:
        data = await self._fetch_info()
        if data:
            val = data.get("lastLoginTime")
            if isinstance(val, int):
                return val
        return None

    @property
    async def last_login_name(self) -> Optional[str]:
        data = await self._fetch_info()
        if data:
            val = data.get("lastLoginName")
            if isinstance(val, str):
                return val
        return None

    @property
    async def rank(self) -> Optional[str]:
        data = await self._fetch_info()
        if data:
            val = data.get("role")
            if isinstance(val, str):
                return val
        return None

    @property
    async def level(self) -> Optional[int]:
        data = await self._fetch_overall()
        if data:
            val = data.get("level")
            if isinstance(val, int):
                return val
        return None

    @property
    async def xp(self) -> Optional[int]:
        data = await self._fetch_overall()
        if data:
            val = data.get("exp")
            if isinstance(val, int):
                return val
        return None

    @property
    async def weighted_wins(self) -> Optional[int]:
        data = await self._fetch_overall()
        if data:
            val = data.get("weightedwins")
            if isinstance(val, int):
                return val
        return None

    @property
    async def game_stats(self) -> Optional[Dict[str, Dict[str, Any]]]:
        data = await self._fetch_game()
        if data:
            val = data.get("stats")
            if isinstance(val, dict):
                return val
        return None

    @property
    async def guild_role(self) -> Optional[str]:
        data = await self._fetch_guild()
        if data:
            val = data.get("guildRole")
            if isinstance(val, str):
                return val
        return None

    @property
    async def guild_join_time(self) -> Optional[int]:
        data = await self._fetch_guild()
        if data:
            val = data.get("joinTime")
            if isinstance(val, int):
                return val
        return None

    @property
    async def guild_id(self) -> Optional[int]:
        data = await self._fetch_guild()
        if data:
            val = data.get("guildId")
            if isinstance(val, int):
                return val
        return None

    async def get_stat_ranking(
        self,
        ref: str,
        type: Literal["wins", "kills", "finals", "beds"]
    ) -> Optional[int]:
        try:
            data = await api.fetch(
                VoxylApiEndpoint.PLAYER_STAT_RANKING,
                uuid=self.uuid,
                ref=ref,
                type=type
            )
            if data and "ranking" in data and isinstance(data["ranking"], int):
                return data["ranking"]
            return None
        except VoxylAPIError:
            return None