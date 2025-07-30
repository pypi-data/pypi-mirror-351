from typing import Optional, Union, List, Dict, Any
from bwpfetcher.client import VoxylAPI
from bwpfetcher.endpoints import VoxylApiEndpoint
from bwpfetcher.exceptions import VoxylAPIError


api = VoxylAPI()

class Guild:
    """
    Represents a Voxyl guild and provides methods to fetch guild info,
    members, and top guild rankings.
    """

    def __init__(self, tag_or_id: Union[str, int]):
        """
        Initialize a Guild using either its tag or ID.

        Args:
            tag_or_id (Union[str, int]): Guild tag (string) or ID (int).
        """
        if isinstance(tag_or_id, int):
            self.query_key = f"-{tag_or_id}"
        else:
            self.query_key = tag_or_id

        self._info: Optional[Dict[str, Any]] = None
        self._members_data: Optional[Dict[str, Any]] = None

    async def _fetch_info(self) -> Optional[Dict[str, Any]]:
        """
        Fetches and caches general guild information.

        Returns:
            Optional[Dict[str, Any]]: Guild info dict or None.
        """
        if self._info is None:
            try:
                self._info = await api.fetch(
                    VoxylApiEndpoint.GUILD_INFO,
                    tag=self.query_key
                )
            except VoxylAPIError as e:
                print(f"Failed to fetch GUILD_INFO for {self.query_key}: {e}")
        return self._info

    async def _fetch_members_data(self) -> Optional[Dict[str, Any]]:
        """
        Fetches and caches full member data.

        Returns:
            Optional[Dict[str, Any]]: Dictionary with 'members' key or None.
        """
        if self._members_data is None:
            try:
                self._members_data = await api.fetch(
                    VoxylApiEndpoint.GUILD_MEMBERS,
                    tag=self.query_key
                )
            except VoxylAPIError as e:
                print(f"Failed to fetch GUILD_MEMBERS for {self.query_key}: {e}")
        return self._members_data

    @property
    async def id(self) -> Optional[int]:
        """
        Returns the guild's ID.
        """
        data = await self._fetch_info()
        return data.get("id") if data and isinstance(data.get("id"), int) else None

    @property
    async def name(self) -> Optional[str]:
        """
        Returns the guild's display name.
        """
        data = await self._fetch_info()
        return data.get("name") if data and isinstance(data.get("name"), str) else None

    @property
    async def description(self) -> Optional[str]:
        """
        Returns the guild's description.
        """
        data = await self._fetch_info()
        return data.get("desc") if data and isinstance(data.get("desc"), str) else None

    @property
    async def xp(self) -> Optional[int]:
        """
        Returns the guild's XP.
        """
        data = await self._fetch_info()
        return data.get("xp") if data and isinstance(data.get("xp"), int) else None

    @property
    async def member_count(self) -> Optional[int]:
        """
        Returns the number of members in the guild.
        """
        data = await self._fetch_info()
        return data.get("num") if data and isinstance(data.get("num"), int) else None

    @property
    async def owner_uuid(self) -> Optional[str]:
        """
        Returns the UUID of the guild owner.
        """
        data = await self._fetch_info()
        return data.get("ownerUUID") if data and isinstance(data.get("ownerUUID"), str) else None

    @property
    async def created_at(self) -> Optional[int]:
        """
        Returns the UNIX timestamp when the guild was created.
        """
        data = await self._fetch_info()
        return data.get("time") if data and isinstance(data.get("time"), int) else None

    @property
    async def members(self) -> Optional[List[Dict[str, Any]]]:
        """
        Returns a list of guild members with their roles and join times.

        Each member dict contains:
            - uuid: str
            - role: str (OWNER, ADMIN, MODERATOR, MEMBER)
            - time: int (UNIX timestamp of join time)

        Returns:
            Optional[List[Dict[str, Any]]]: Member list.
        """
        data = await self._fetch_members_data()
        return data.get("members") if data and isinstance(data.get("members"), list) else None

    @staticmethod
    async def top_guilds(num: int = 100) -> Optional[List[Dict[str, Any]]]:
        """
        Returns a list of the top guilds sorted by XP.

        Args:
            num (int): Number of top guilds to return (max 100).

        Returns:
            Optional[List[Dict[str, Any]]]: List of top guilds.
        """
        try:
            result = await api.fetch(VoxylApiEndpoint.GUILD_TOP, num=num)
            return result.get("guilds") if result and isinstance(result.get("guilds"), list) else None
        except VoxylAPIError as e:
            print(f"Failed to fetch GUILD_TOP: {e}")
            return None