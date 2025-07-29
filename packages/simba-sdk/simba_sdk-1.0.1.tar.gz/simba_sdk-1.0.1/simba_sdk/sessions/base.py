from dataclasses import dataclass, fields

from typing_extensions import Dict, List, Optional, Self, Type, Union

from simba_sdk.config import Settings
from simba_sdk.core.requests.auth.token_store import InMemoryTokenStore
from simba_sdk.core.requests.client.base import Client


@dataclass
class Base:
    @classmethod
    def from_dict(cls, kwargs: Dict[str, str]):
        """
        Use this method instead of __init__ to ignore extra args
        """
        field_names = [f.name for f in fields(cls)]
        return cls(**{k: v for k, v in kwargs.items() if k in field_names})


class BaseSession:
    def __init__(
        self,
        settings: Optional[Settings] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        **kwargs: str,
    ) -> None:
        if settings is None:
            self.client_id = client_id
            self.client_secret = client_secret
            if client_id:
                kwargs["client_id"] = client_id
            if client_secret:
                kwargs["client_secret"] = client_secret
            self.settings = Settings(**kwargs)
        else:
            self.settings = settings
        self._store = InMemoryTokenStore()
        self._clients: Dict[str, Union[Type[Client], Client]] = {}

    async def _authorise(self):
        for service, client in self._clients.items():
            self._clients[service] = client(
                name=service,
                settings=self.settings,
                token_store=self._store,
            )
            await self._clients[service].authorise(self.settings.token_url)

    async def __aenter__(self) -> Self:
        self._registry: List[BaseSession] = []
        await self._authorise()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._clients = None
        for child in self._registry:
            await child.__aexit__(exc_type, exc_val, exc_tb)
        self._registry = []
