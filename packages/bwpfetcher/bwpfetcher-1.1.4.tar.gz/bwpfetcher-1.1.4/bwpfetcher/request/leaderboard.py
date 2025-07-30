from typing import Optional, List, Dict, Literal
from bwpfetcher.client import VoxylAPI
from bwpfetcher.endpoints import VoxylApiEndpoint
from bwpfetcher.exceptions import VoxylAPIError


api = VoxylAPI()

class Leaderboard:
    """Handles leaderboard endpoints including normal, technique, and game leaderboards."""

    _normal_cache: Dict[str, List[Dict[str, any]]] = {}
    _technique_cache: Dict[str, List[Dict[str, any]]] = {}
    _game_cache: Dict[str, Dict[str, List[Dict[str, any]]]] = {}

    @staticmethod
    async def get_normal(type: Literal["weightedwins", "level"], num: int = 100) -> Optional[List[Dict[str, any]]]:
        """
        Retrieves the normal leaderboard (weightedwins or level).

        Args:
            type (Literal): Type of leaderboard to retrieve.
            num (int): Number of entries to retrieve (max 100).

        Returns:
            Optional[List[Dict[str, any]]]: List of leaderboard entries or fallback from cache.
        """
        try:
            data = await api.fetch(VoxylApiEndpoint.LEADERBOARD_NORMAL, type=type, num=num)
            Leaderboard._normal_cache[type] = data.get("players", [])
            return Leaderboard._normal_cache[type]
        except VoxylAPIError as e:
            print(f"Failed to fetch normal leaderboard ({type}): {e}")
            return Leaderboard._normal_cache.get(type)

    @staticmethod
    async def get_technique(technique: str) -> Optional[List[Dict[str, any]]]:
        """
        Retrieves leaderboard data for a specific technique.

        Args:
            technique (str): Technique name.

        Returns:
            Optional[List[Dict[str, any]]]: List of leaderboard entries or fallback from cache.
        """
        try:
            data = await api.fetch(VoxylApiEndpoint.LEADERBOARD_TECHNIQUE, technique=technique)
            Leaderboard._technique_cache[technique] = data.get("players", [])
            return Leaderboard._technique_cache[technique]
        except VoxylAPIError as e:
            print(f"Failed to fetch technique leaderboard ({technique}): {e}")
            return Leaderboard._technique_cache.get(technique)

    @staticmethod
    async def get_game(ref: str, period: Literal["weekly", "daily"], type: Literal["wins", "winstreaks"]) -> Optional[List[Dict[str, any]]]:
        """
        Retrieves leaderboard for a specific game and period.

        Args:
            ref (str): Game reference ID.
            period (Literal): Time period ('weekly' or 'daily').
            type (Literal): Stat type ('wins' or 'winstreaks').

        Returns:
            Optional[List[Dict[str, any]]]: List of leaderboard entries or fallback from cache.
        """
        try:
            data = await api.fetch(VoxylApiEndpoint.LEADERBOARD_GAME, ref=ref, period=period, type=type)
            if ref not in Leaderboard._game_cache:
                Leaderboard._game_cache[ref] = {}
            Leaderboard._game_cache[ref][type] = data.get("players", [])
            return Leaderboard._game_cache[ref][type]
        except VoxylAPIError as e:
            print(f"Failed to fetch game leaderboard ({ref}, {type}): {e}")
            return Leaderboard._game_cache.get(ref, {}).get(type)