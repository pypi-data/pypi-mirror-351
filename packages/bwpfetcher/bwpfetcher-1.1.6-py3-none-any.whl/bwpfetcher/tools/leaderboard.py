from typing import Optional, List, Dict, Literal
from bwpfetcher.client import VoxylAPI
from bwpfetcher.endpoints import VoxylApiEndpoint
from bwpfetcher.exceptions import VoxylAPIError

api = VoxylAPI()

class Leaderboard:
    """Handles leaderboard endpoints including normal, technique, and game leaderboards."""

    @staticmethod
    async def get_normal(
        type: Literal["weightedwins", "level"], 
        num: int = 100
    ) -> Optional[List[Dict[str, any]]]:
        """
        Retrieves the normal leaderboard (weightedwins or level).

        Args:
            type (Literal): Type of leaderboard to retrieve.
            num (int): Number of entries to retrieve (max 100).

        Returns:
            Optional[List[Dict[str, any]]]: List of leaderboard entries or None.
        """
        try:
            data = await api.fetch(VoxylApiEndpoint.LEADERBOARD_NORMAL, type=type, num=num)
            return data.get("players", []) if data else None
        
        except VoxylAPIError:
            return None

    @staticmethod
    async def get_technique(
        technique: str
    ) -> Optional[List[Dict[str, any]]]:
        """
        Retrieves leaderboard data for a specific technique.

        Args:
            technique (str): Technique name.

        Returns:
            Optional[List[Dict[str, any]]]: List of leaderboard entries or None.
        """
        try:
            data = await api.fetch(VoxylApiEndpoint.LEADERBOARD_TECHNIQUE, technique=technique)
            return data.get("players", []) if data else None
        
        except VoxylAPIError:
            return None

    @staticmethod
    async def get_game(
        ref: str, 
        period: Literal["weekly", "daily"], 
        type: Literal["wins", "winstreaks"]
    ) -> Optional[List[Dict[str, any]]]:
        """
        Retrieves leaderboard for a specific game and period.

        Args:
            ref (str): Game reference ID.
            period (Literal): Time period ('weekly' or 'daily').
            type (Literal): Stat type ('wins' or 'winstreaks').

        Returns:
            Optional[List[Dict[str, any]]]: List of leaderboard entries or None.
        """
        try:
            data = await api.fetch(VoxylApiEndpoint.LEADERBOARD_GAME, ref=ref, period=period, type=type)
            return data.get("players", []) if data else None
        
        except VoxylAPIError:
            return None