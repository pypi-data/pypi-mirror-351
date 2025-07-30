from typing import Optional, List, Dict, Any
from bwpfetcher.client import VoxylAPI
from bwpfetcher.endpoints import VoxylApiEndpoint

api = VoxylAPI()

class Achievements:
    """
    Always fetches fresh data from the API on property access.
    """

    def __init__(self, uuid: Optional[str] = None):
        self.uuid = uuid

    async def _fetch_player_achievements(self, uuid: str) -> Optional[List[str]]:
        try:
            data = await api.fetch(VoxylApiEndpoint.PLAYER_ACHIEVEMENTS, uuid=uuid)
            return data.get("achievements", []) if data else None
        except Exception:
            return None

    async def _fetch_all_achievements(self) -> Optional[List[Dict[str, Any]]]:
        try:
            data = await api.fetch(VoxylApiEndpoint.ALL_ACHIEVEMENTS)
            return data.get("info", []) if data else None
        except Exception:
            return None

    async def player_achievements(self) -> Optional[List[str]]:
        """
        Simulates a property that fetches fresh achievements each time.
        """
        if self.uuid is None:
            return None
        
        return await self._fetch_player_achievements(self.uuid)

    async def all_info(self) -> Optional[List[Dict[str, Any]]]:
        """
        Simulates a property that fetches fresh achievement info each time.
        """
        return await self._fetch_all_achievements()

    async def get_achievement_info(self, achievement_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves fresh detailed info for a specific achievement.
        """
        info = await self.all_info()
        if info:
            for achievement in info:
                if achievement.get("id") == achievement_id:
                    return achievement
        return None