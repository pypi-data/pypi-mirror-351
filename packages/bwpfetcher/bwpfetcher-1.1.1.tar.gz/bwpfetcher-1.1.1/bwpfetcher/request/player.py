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
        self._player_info: Optional[Dict[str, Any]] = None
        self._player_overall: Optional[Dict[str, Any]] = None
        self._player_game: Optional[Dict[str, Any]] = None
        self._player_guild: Optional[Dict[str, Any]] = None

    async def _fetch_info(self) -> Optional[Dict[str, Any]]:
        """
        Fetches player info from the PLAYER_INFO endpoint and caches it.

        Returns:
            Optional[Dict[str, Any]]: Player info data or None if the fetch fails.
        """
        if self._player_info is None:
            try:
                self._player_info = await api.fetch(VoxylApiEndpoint.PLAYER_INFO, uuid=self.uuid)
            except VoxylAPIError as e:
                print(f"Failed to fetch PLAYER_INFO for {self.uuid}: {e}")
        return self._player_info

    async def _fetch_overall(self) -> Optional[Dict[str, Any]]:
        """
        Fetches overall player data such as level, XP, and wins.

        Returns:
            Optional[Dict[str, Any]]: Player overall data or None if the fetch fails.
        """
        if self._player_overall is None:
            try:
                self._player_overall = await api.fetch(VoxylApiEndpoint.PLAYER_OVERALL, uuid=self.uuid)
            except VoxylAPIError as e:
                print(f"Failed to fetch PLAYER_OVERALL for {self.uuid}: {e}")
        return self._player_overall

    async def _fetch_game(self) -> Optional[Dict[str, Any]]:
        """
        Fetches per-game player statistics.

        Returns:
            Optional[Dict[str, Any]]: Player game stats or None if the fetch fails.
        """
        if self._player_game is None:
            try:
                self._player_game = await api.fetch(VoxylApiEndpoint.PLAYER_GAME, uuid=self.uuid)
            except VoxylAPIError as e:
                print(f"Failed to fetch PLAYER_GAME for {self.uuid}: {e}")
        return self._player_game

    async def _fetch_guild(self) -> Optional[Dict[str, Any]]:
        """
        Fetches guild-related player data.

        Returns:
            Optional[Dict[str, Any]]: Guild data or None if the fetch fails.
        """
        if self._player_guild is None:
            try:
                self._player_guild = await api.fetch(VoxylApiEndpoint.PLAYER_GUILD, uuid=self.uuid)
            except VoxylAPIError as e:
                print(f"Failed to fetch PLAYER_GUILD for {self.uuid}: {e}")
        return self._player_guild

    @property
    async def last_login_time(self) -> Optional[int]:
        """
        Returns the last login time as a UNIX timestamp.
        """
        data = await self._fetch_info()
        if data:
            val = data.get("lastLoginTime")
            if isinstance(val, int):
                return val
        return None

    @property
    async def last_login_name(self) -> Optional[str]:
        """
        Returns the name the player last used to log in.
        """
        data = await self._fetch_info()
        if data:
            val = data.get("lastLoginName")
            if isinstance(val, str):
                return val
        return None

    @property
    async def rank(self) -> Optional[str]:
        """
        Returns the player's current rank or role.
        """
        data = await self._fetch_info()
        if data:
            val = data.get("role")
            if isinstance(val, str):
                return val
        return None

    @property
    async def level(self) -> Optional[int]:
        """
        Returns the player's current level.
        """
        data = await self._fetch_overall()
        if data:
            val = data.get("level")
            if isinstance(val, int):
                return val
        return None

    @property
    async def xp(self) -> Optional[int]:
        """
        Returns the total experience points (XP) the player has earned.
        """
        data = await self._fetch_overall()
        if data:
            val = data.get("exp")
            if isinstance(val, int):
                return val
        return None

    @property
    async def weighted_wins(self) -> Optional[int]:
        """
        Returns the player's weighted win score.
        """
        data = await self._fetch_overall()
        if data:
            val = data.get("weightedwins")
            if isinstance(val, int):
                return val
        return None

    @property
    async def game_stats(self) -> Optional[Dict[str, Dict[str, Any]]]:
        """
        Returns detailed statistics for each game the player has participated in.
        """
        data = await self._fetch_game()
        if data:
            val = data.get("stats")
            if isinstance(val, dict):
                return val
        return None

    @property
    async def guild_role(self) -> Optional[str]:
        """
        Returns the player's role within their current guild.
        """
        data = await self._fetch_guild()
        if data:
            val = data.get("guildRole")
            if isinstance(val, str):
                return val
        return None

    @property
    async def guild_join_time(self) -> Optional[int]:
        """
        Returns the timestamp of when the player joined their guild.
        """
        data = await self._fetch_guild()
        if data:
            val = data.get("joinTime")
            if isinstance(val, int):
                return val
        return None

    @property
    async def guild_id(self) -> Optional[int]:
        """
        Returns the ID of the guild the player belongs to.
        """
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
        """
        Returns the player's global stat ranking for a given reference and type.
        
        Args:
            ref (str): Reference for the ranking (e.g., game or mode name).
            type (Literal["wins", "kills", "finals", "beds"]): Type of stat ranking.

        Returns:
            Optional[int]: The ranking position or None if unavailable.
        """
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
        except VoxylAPIError as e:
            print(f"Failed to get stat ranking for {self.uuid}: {e}")
            return None
