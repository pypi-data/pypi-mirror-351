import os
import aiohttp
from typing import Any, Optional
from .endpoints import VoxylApiEndpoint
from .exceptions import (
    VoxylAPIError,
    VoxylRateLimitError,
    VoxylClientError,
    VoxylUnexpectedStatusError,
    VoxylInvalidRequestError,
    VoxylNotFoundError,
)
from dotenv import load_dotenv

load_dotenv()

class VoxylAPI:
    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key: str = api_key or os.getenv("API_KEY") or ""
        self.base_url: str = "https://api.voxyl.net"
        if not self.api_key:
            raise VoxylAPIError("API key must be provided either via environment or constructor.")

    async def fetch(
        self,
        endpoint: VoxylApiEndpoint,
        *,
        session: Optional[aiohttp.ClientSession] = None,
        **kwargs: Any
    ) -> dict:
        url: str = f"{self.base_url}/{endpoint.value.format(**kwargs)}"
        params: dict[str, Any] = {"api": self.api_key}

        query_params = {k: v for k, v in kwargs.items() if k not in url}
        params.update(query_params)

        own_session: bool = session is None
        session = session or aiohttp.ClientSession()

        try:
            async with session.get(url, params=params) as response:
                status = response.status

                if status == 200:
                    return await response.json(content_type=None)
                elif status == 400:
                    raise VoxylInvalidRequestError()
                elif status == 404:
                    raise VoxylNotFoundError(url)
                elif status == 429:
                    raise VoxylRateLimitError()
                elif 500 <= status < 600:
                    raise VoxylUnexpectedStatusError(status, "Server error occurred.")
                else:
                    raise VoxylUnexpectedStatusError(status)

        except aiohttp.ClientError as e:
            raise VoxylClientError(str(e)) from e
        
        finally:
            if own_session:
                await session.close()