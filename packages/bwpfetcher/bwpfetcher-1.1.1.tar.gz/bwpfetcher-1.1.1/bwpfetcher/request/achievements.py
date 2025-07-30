from typing import Optional, List, Dict, Any
from bwpfetcher.client import VoxylAPI
from bwpfetcher.endpoints import VoxylApiEndpoint
from bwpfetcher.exceptions import VoxylAPIError

api = VoxylAPI()

class Achievements:
    """
    Handles retrieval and caching of player achievements and all achievements info.

    Can fetch achievements for a specific player by UUID, fetch all available achievements info,
    and retrieve detailed info about a specific achievement by its ID.
    """

    def __init__(self, uuid: Optional[str] = None):
        """
        Initializes the Achievements handler.

        Args:
            uuid (Optional[str]): The UUID of the player whose achievements to manage.
        """
        self.uuid = uuid
        self._player_achievements: Optional[List[str]] = None
        self._all_achievements_info: Optional[List[Dict[str, Any]]] = None

    async def fetch_player_achievements(self, uuid: str) -> Optional[List[str]]:
        """
        Fetches the list of achievement IDs for a given player UUID from the API.

        Args:
            uuid (str): The UUID of the player.

        Returns:
            Optional[List[str]]: List of achievement IDs the player has, or None if an error occurs.
        """
        try:
            data = await api.fetch(VoxylApiEndpoint.PLAYER_ACHIEVEMENTS, uuid=uuid)
            return data.get("achievements", []) if data else None
        except Exception as error:
            print(f"Error fetching player achievements: {error}")
            return None

    async def fetch_all_achievements(self) -> Optional[List[Dict[str, Any]]]:
        """
        Fetches all available achievements info from the API.

        Returns:
            Optional[List[Dict[str, Any]]]: List of achievement info objects or None if an error occurs.
        """
        try:
            data = await api.fetch(VoxylApiEndpoint.ALL_ACHIEVEMENTS)
            return data.get("info", []) if data else None
        except Exception as error:
            print(f"Error fetching all achievements info: {error}")
            return None

    @property
    async def player_achievements(self) -> Optional[List[str]]:
        """
        Cached property to get the player's achievements list.

        If the achievements are not already fetched, it will fetch them using the player's UUID.

        Returns:
            Optional[List[str]]: List of achievement IDs or None if UUID is not set or an error occurs.
        """
        if self.uuid is None:
            print("UUID not set.")
            return None
        if self._player_achievements is None:
            self._player_achievements = await self.fetch_player_achievements(self.uuid)
        return self._player_achievements

    @property
    async def all_info(self) -> Optional[List[Dict[str, Any]]]:
        """
        Cached property to get all achievements info.

        Fetches from the API on first access, then caches the result.

        Returns:
            Optional[List[Dict[str, Any]]]: List of all achievement info dictionaries or None if error occurs.
        """
        if self._all_achievements_info is None:
            self._all_achievements_info = await self.fetch_all_achievements()
        return self._all_achievements_info

    async def get_achievement_info(self, achievement_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves detailed info for a specific achievement by its ID.

        Args:
            achievement_id (int): The ID of the achievement to look up.

        Returns:
            Optional[Dict[str, Any]]: Achievement info dictionary if found, else None.
        """
        info = await self.all_info
        if info:
            for achievement in info:
                if achievement.get("id") == achievement_id:
                    return achievement
        return None
