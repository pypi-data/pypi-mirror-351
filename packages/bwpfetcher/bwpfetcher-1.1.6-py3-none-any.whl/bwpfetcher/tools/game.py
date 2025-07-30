from typing import Optional, List, Dict, Any
from bwpfetcher.client import VoxylAPI
from bwpfetcher.endpoints import VoxylApiEndpoint
from bwpfetcher.exceptions import VoxylAPIError

api = VoxylAPI()

class Game:
    """
    Represents detailed information about a game retrieved by its UUID.
    """

    def __init__(self, uuid: str):
        """
        Initializes the Game instance with the specified game UUID.

        Args:
            uuid (str): The UUID of the game to retrieve information for.
        """
        self.uuid = uuid

    async def _fetch_data(self) -> Optional[Dict[str, Any]]:
        """
        Fetches the game data from the API.

        Returns:
            Optional[Dict[str, Any]]: Game data or None if request fails.
        """
        try:
            return await api.fetch(VoxylApiEndpoint.GAME_INFO, uuid=self.uuid)
        except VoxylAPIError:
            return None

    async def _fetch_status_data(self) -> Optional[Dict[str, Any]]:
        """
        Fetches the game status data from the API.

        Returns:
            Optional[Dict[str, Any]]: Status data or None if request fails.
        """
        try:
            return await api.fetch(VoxylApiEndpoint.GAME_STATUS, uuid=self.uuid)
        except VoxylAPIError:
            return None

    @property
    async def active(self) -> Optional[bool]:
        data = await self._fetch_status_data()
        val = data.get("active") if data else None
        return val if isinstance(val, bool) else None

    @property
    async def winnerUUID(self) -> Optional[str]:
        data = await self._fetch_data()
        val = data.get("winnerUUID") if data else None
        return val if val is None or isinstance(val, str) else None

    @property
    async def winningTeamId(self) -> Optional[int]:
        data = await self._fetch_data()
        val = data.get("winningTeamId") if data else None
        return val if isinstance(val, int) else None

    @property
    async def ref(self) -> Optional[str]:
        data = await self._fetch_data()
        val = data.get("ref") if data else None
        return val if isinstance(val, str) else None

    @property
    async def timeStarted(self) -> Optional[int]:
        data = await self._fetch_data()
        val = data.get("timeStarted") if data else None
        return val if isinstance(val, int) else None

    @property
    async def numberOfPlayers(self) -> Optional[int]:
        data = await self._fetch_data()
        val = data.get("numberOfPlayers") if data else None
        return val if isinstance(val, int) else None

    @property
    async def numberOfTeams(self) -> Optional[int]:
        data = await self._fetch_data()
        val = data.get("numberOfTeams") if data else None
        return val if isinstance(val, int) else None

    @property
    async def secondsRunning(self) -> Optional[int]:
        data = await self._fetch_data()
        val = data.get("secondsRunning") if data else None
        return val if isinstance(val, int) else None

    @property
    async def totalKills(self) -> Optional[int]:
        data = await self._fetch_data()
        val = data.get("totalKills") if data else None
        return val if isinstance(val, int) else None

    @property
    async def totalFinals(self) -> Optional[int]:
        data = await self._fetch_data()
        val = data.get("totalFinals") if data else None
        return val if isinstance(val, int) else None

    @property
    async def midGameDisconnects(self) -> Optional[int]:
        data = await self._fetch_data()
        val = data.get("midGameDisconnects") if data else None
        return val if isinstance(val, int) else None

    @property
    async def mapID(self) -> Optional[int]:
        data = await self._fetch_data()
        val = data.get("mapID") if data else None
        return val if isinstance(val, int) else None

    @property
    async def serverName(self) -> Optional[str]:
        data = await self._fetch_data()
        val = data.get("serverName") if data else None
        return val if isinstance(val, str) else None

    async def get_players(self) -> Optional[List[Dict[str, Any]]]:
        data = await self._fetch_data()
        if data and isinstance(data.get("players"), list):
            return data["players"]
        return None
