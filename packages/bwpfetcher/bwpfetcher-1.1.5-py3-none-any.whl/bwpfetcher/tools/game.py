from typing import Optional, List, Dict, Any
from bwpfetcher.client import VoxylAPI
from bwpfetcher.endpoints import VoxylApiEndpoint
from bwpfetcher.exceptions import VoxylAPIError

api = VoxylAPI()

class Game:
    """
    Represents detailed information about a game retrieved by its UUID.

    Provides async properties for accessing summary fields of the game such as winner UUID,
    number of players, game duration, etc. Also provides a method to get the list of
    players with detailed statistics.
    """

    def __init__(self, uuid: str):
        """
        Initializes the GameInfo instance with the specified game UUID.

        Args:
            uuid (str): The UUID of the game to retrieve information for.
        """
        self.uuid = uuid
        self._data: Optional[Dict[str, Any]] = None
        self._status_data: Optional[Dict[str, Any]] = None

    async def _fetch_data(self) -> Optional[Dict[str, Any]]:
        """
        Fetches the game data from the API if not already cached.

        Returns:
            Optional[Dict[str, Any]]: The full game data dictionary if successful, None otherwise.
        """
        if self._data is None:
            try:
                self._data = await api.fetch(VoxylApiEndpoint.GAME_INFO, uuid=self.uuid)
            except VoxylAPIError as e:
                print(f"Failed to fetch game info for {self.uuid}: {e}")
        return self._data

    async def _fetch_status_data(self) -> Optional[Dict[str, Any]]:
        """
        Fetches the game status data from the API if not already cached.

        Returns:
            Optional[Dict[str, Any]]: The game status data dictionary if successful, None otherwise.
        """
        if self._status_data is None:
            try:
                self._status_data = await api.fetch(VoxylApiEndpoint.GAME_STATUS, uuid=self.uuid)
            except VoxylAPIError as e:
                print(f"Failed to fetch game status for {self.uuid}: {e}")
        return self._status_data

    @property
    async def active(self) -> Optional[bool]:
        """
        Indicates whether the game is currently active.

        Returns:
            Optional[bool]: True if active, False if inactive, None if status could not be retrieved.
        """
        data = await self._fetch_status_data()
        val = data.get("active") if data else None
        if isinstance(val, bool):
            return val
        return None

    @property
    async def winnerUUID(self) -> Optional[str]:
        """
        The UUID of the winner of the game. May be None if no winner.

        Returns:
            Optional[str]: Winner UUID or None.
        """
        data = await self._fetch_data()
        val = data.get("winnerUUID") if data else None
        if val is None or isinstance(val, str):
            return val
        return None

    @property
    async def winningTeamId(self) -> Optional[int]:
        """
        The ID of the winning team. -1 if there were no winners.

        Returns:
            Optional[int]: Winning team ID or None.
        """
        data = await self._fetch_data()
        val = data.get("winningTeamId") if data else None
        if isinstance(val, int):
            return val
        return None

    @property
    async def ref(self) -> Optional[str]:
        """
        The game reference string. Use `/join list` in-game for valid references.

        Returns:
            Optional[str]: Game reference or None.
        """
        data = await self._fetch_data()
        val = data.get("ref") if data else None
        if isinstance(val, str):
            return val
        return None

    @property
    async def timeStarted(self) -> Optional[int]:
        """
        The UNIX timestamp (in seconds) when the game started.

        Returns:
            Optional[int]: Start time as UNIX timestamp or None.
        """
        data = await self._fetch_data()
        val = data.get("timeStarted") if data else None
        if isinstance(val, int):
            return val
        return None

    @property
    async def numberOfPlayers(self) -> Optional[int]:
        """
        The number of players who participated in the game.

        Returns:
            Optional[int]: Number of players or None.
        """
        data = await self._fetch_data()
        val = data.get("numberOfPlayers") if data else None
        if isinstance(val, int):
            return val
        return None

    @property
    async def numberOfTeams(self) -> Optional[int]:
        """
        The number of teams in the game.

        Returns:
            Optional[int]: Number of teams or None.
        """
        data = await self._fetch_data()
        val = data.get("numberOfTeams") if data else None
        if isinstance(val, int):
            return val
        return None

    @property
    async def secondsRunning(self) -> Optional[int]:
        """
        Duration of the game in seconds.

        Returns:
            Optional[int]: Seconds the game ran or None.
        """
        data = await self._fetch_data()
        val = data.get("secondsRunning") if data else None
        if isinstance(val, int):
            return val
        return None

    @property
    async def totalKills(self) -> Optional[int]:
        """
        The combined total of kills during the game.

        Returns:
            Optional[int]: Total kills or None.
        """
        data = await self._fetch_data()
        val = data.get("totalKills") if data else None
        if isinstance(val, int):
            return val
        return None

    @property
    async def totalFinals(self) -> Optional[int]:
        """
        The combined total of final kills during the game.

        Returns:
            Optional[int]: Total final kills or None.
        """
        data = await self._fetch_data()
        val = data.get("totalFinals") if data else None
        if isinstance(val, int):
            return val
        return None

    @property
    async def midGameDisconnects(self) -> Optional[int]:
        """
        Number of times players disconnected during the game.

        Returns:
            Optional[int]: Mid-game disconnect count or None.
        """
        data = await self._fetch_data()
        val = data.get("midGameDisconnects") if data else None
        if isinstance(val, int):
            return val
        return None

    @property
    async def mapID(self) -> Optional[int]:
        """
        The ID of the map the game was played on.

        Returns:
            Optional[int]: Map ID or None.
        """
        data = await self._fetch_data()
        val = data.get("mapID") if data else None
        if isinstance(val, int):
            return val
        return None

    @property
    async def serverName(self) -> Optional[str]:
        """
        The server name the game was played on.

        Returns:
            Optional[str]: Server name or None.
        """
        data = await self._fetch_data()
        val = data.get("serverName") if data else None
        if isinstance(val, str):
            return val
        return None

    async def get_players(self) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieves the list of players who participated in the game along with their stats.

        Returns:
            Optional[List[Dict[str, Any]]]: List of player dictionaries or None if unavailable.
        """
        data = await self._fetch_data()
        if data and "players" in data and isinstance(data["players"], list):
            return data["players"]
        return None
