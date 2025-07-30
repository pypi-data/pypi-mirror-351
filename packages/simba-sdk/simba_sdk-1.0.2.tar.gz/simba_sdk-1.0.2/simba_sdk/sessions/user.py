from dataclasses import dataclass
from typing import Union
from uuid import UUID

from simba_sdk.core.requests.client.members.client import MembersClient
from simba_sdk.core.requests.client.members.schemas import CreateDomainInput
from simba_sdk.sessions import parse
from simba_sdk.sessions.base import Base, BaseSession
from simba_sdk.sessions.domain import Account, Domain, DomainSession


@dataclass
class User(Base):
    email: str
    simba_id: str
    first_name: str
    last_name: str


class UserSession(BaseSession):
    def __init__(self, **kwargs: str) -> None:
        """
        For kwargs see BaseSession.__init__
        """
        super().__init__(**kwargs)
        self._clients = {"members": MembersClient}

    async def __aenter__(self):
        await super().__aenter__()
        whoami = await self._clients["members"].whoami()
        user_dict = whoami.model_dump()
        user_dict["first_name"] = user_dict["profile"]["first_name"]
        user_dict["last_name"] = user_dict["profile"]["last_name"]
        self.user = User.from_dict(user_dict)
        return self

    @parse(Domain)
    async def create_domain(self, domain: Domain) -> DomainSession:
        domain_input = CreateDomainInput(
            display_name=domain.display_name,
            name=domain.name,
        )
        await self._clients["members"].create_domain(createdomaininput=domain_input)
        return await self.get_domain(domain.name)

    async def get_domain(
        self, domain: str, account: Union[UUID, Account, None] = None
    ) -> DomainSession:
        domain_session = DomainSession(
            name=domain, account=account, settings=self.settings
        )
        domain_session.user = self.user
        return domain_session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.user = None
        self.account = None
        await super().__aexit__(exc_type, exc_val, exc_tb)
