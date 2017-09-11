from aiohttp import web
from kong.routes import setup_routes
import aiohttp_autoreload

aiohttp_autoreload.start()

app = web.Application()
setup_routes(app)

web.run_app(app, host='0.0.0.0', port=80)
