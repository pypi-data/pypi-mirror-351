from typing import List, Dict, Any, Optional
from bwpfetcher.client import VoxylAPI
from bwpfetcher.endpoints import VoxylApiEndpoint
from bwpfetcher.exceptions import VoxylAPIError

api = VoxylAPI()

class Announcements:
    """
    Represents a collection of announcements from the Voxyl API.
    Provides access to all current announcements.
    """

    def __init__(self):
        """
        Initializes the Announcements manager.
        """
        pass  # No cache needed

    async def _fetch_all(self) -> Optional[List[Dict[str, Any]]]:
        """
        Fetches all announcements from the API.

        Returns:
            Optional[List[Dict[str, Any]]]: A list of announcements or None if the fetch fails.
        """
        try:
            return await api.fetch(VoxylApiEndpoint.ALL_ANNOUNCEMENTS)
        except VoxylAPIError:
            return None

    @property
    async def all(self) -> Optional[List[Dict[str, Any]]]:
        """
        Returns all announcements.

        Returns:
            Optional[List[Dict[str, Any]]]: A list of announcement dictionaries.
        """
        return await self._fetch_all()

    async def get_titles(self) -> Optional[List[str]]:
        """
        Returns a list of all announcement titles.

        Returns:
            Optional[List[str]]: Titles of announcements.
        """
        data = await self._fetch_all()
        if data:
            return [a.get("title") for a in data if isinstance(a.get("title"), str)]
        return None

    async def get_by_id(self, announcement_id: int) -> Optional[Dict[str, Any]]:
        """
        Gets a specific announcement by its ID.

        Args:
            announcement_id (int): The ID of the announcement to retrieve.

        Returns:
            Optional[Dict[str, Any]]: The announcement data or None if not found.
        """
        data = await self._fetch_all()
        if data:
            for announcement in data:
                if announcement.get("id") == announcement_id:
                    return announcement
        return None