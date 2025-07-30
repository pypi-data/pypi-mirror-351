import aiohttp

class HTTPSessionManager:
    def __init__(self):
        self._session: aiohttp.ClientSession| None = None

    def get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close_session(self):
        if self._session:
            await self._session.close()
            self._session = None