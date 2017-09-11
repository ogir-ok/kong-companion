import asyncio
from aiohttp import web

from .checkers import CHECKERS


async def index(request):
    """
    Performs kong health check
    """

    sync_checkers = [c for c in CHECKERS if not c.run_async]
    async_checkers = [c for c in CHECKERS if c.run_async]

    res = {}

    for c in sync_checkers:
        checker, status = await c()
        res[checker] = status
        if not status and c.stop_on_failure:
            return web.json_response(data=res)

    results = await asyncio.gather(*[c() for c in async_checkers])

    for checker, status in results:
        res[checker] = status

    return web.json_response(data=res)


