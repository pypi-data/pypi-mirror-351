from typing import Optional
from bwpfetcher.client import VoxylAPI
from bwpfetcher.endpoints import VoxylApiEndpoint
from bwpfetcher.exceptions import VoxylAPIError

api = VoxylAPI()

class Integration:
    """
    Provides access to integration information between Minecraft player UUIDs
    and Discord account IDs via Voxyl API endpoints.
    """

    def __init__(self, uuid: Optional[str] = None, discord_id: Optional[str] = None):
        """
        Initializes the Integration instance.

        Args:
            uuid (Optional[str]): The UUID of the Minecraft player.
            discord_id (Optional[str]): The Discord account ID.
        """
        self.uuid = uuid
        self.discord_id = discord_id

    @property
    async def discord_id_from_player(self) -> Optional[str]:
        """
        Fetches the Discord ID associated with the Minecraft player UUID.

        Returns:
            Optional[str]: The Discord ID if found, None otherwise.
        """
        if self.uuid is None:
            return None

        try:
            data = await api.fetch(VoxylApiEndpoint.DISCORD_FROM_PLAYER, uuid=self.uuid)
            discord_id = data.get("id") if data else None
            return discord_id if isinstance(discord_id, str) else None
        except VoxylAPIError:
            return None

    @property
    async def player_uuid_from_discord(self) -> Optional[str]:
        """
        Fetches the Minecraft player UUID associated with the Discord ID.

        Returns:
            Optional[str]: The player UUID if found, None otherwise.
        """
        if self.discord_id is None:
            return None

        try:
            data = await api.fetch(VoxylApiEndpoint.PLAYER_FROM_DISCORD, id=self.discord_id)
            player_uuid = data.get("uuid") if data else None
            return player_uuid if isinstance(player_uuid, str) else None
        except VoxylAPIError:
            return None