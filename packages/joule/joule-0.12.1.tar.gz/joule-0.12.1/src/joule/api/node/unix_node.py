from typing import List
from .base_node import BaseNode
from .tcp_node import TcpNode
from joule.api.session import UnixSession
from joule.constants import EndPoints

class UnixNode(BaseNode):

    def __init__(self, name: str, path: str, cafile: str = ""):
        self._path = path
        session = UnixSession(path, cafile)
        super().__init__(name, session)
        self.url = "http://joule.localhost"

    def __repr__(self):
        return "<joule.api.node.UnixNode path=\"%s\">" % self._path

    async def follower_list(self) -> List[BaseNode]:
        resp = await self.session.get(EndPoints.followers)
        return [TcpNode(item['name'], item['location'], item['key'], self.session.cafile) for item in resp]