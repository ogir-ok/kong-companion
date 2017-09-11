import aiohttp

from config import config

from .client import KongClient
from .apis import get_apis_from_docker, KongApi


class Checker:
    """
    Kong checker
    """

    # by default run all checkers async
    run_async = True
    # stop checks if this is failed
    stop_on_failure = False

    def __init__(self):
        pass

    async def perform_check(self, *args, **kwargs):
        raise NotImplemented

    async def __call__(self, *args, **kwargs):
        return self.name, await self.perform_check()

    @property
    def name(self):
        return self.__class__.__name__


class Acting(Checker):
    run_async = False
    stop_on_failure = True

    async def perform_check(self, *args, **kwargs):
        try:
            with KongClient() as kc:
                resp = await kc.plugins.get()
                if resp.status == 200:
                    return True
        except aiohttp.client_exceptions.ClientConnectorError:
            return False
        return False


class Plugins(Checker):

    async def perform_check(self, *args, **kwargs):
        with KongClient() as kc:
            resp = await kc.plugins.get()
            installed_plugins = await resp.json()

            plugins = config.get('plugins', [])
            for plugin in plugins:
                await kc.plugins.post(json=plugin)

            return installed_plugins
        return False


class Consumers(Checker):

    async def perform_check(self, *args, **kwargs):
        with KongClient() as kc:
            consumers = config.get('consumers', [])
            for consumer in consumers:
                resp = await kc.consumers.url(consumer['id']).get()
                if resp.status == 404:
                    await kc.consumers.post(json=consumer)
            return consumers
        return False


class Apis(Checker):

    async def perform_check(self, *args, **kwargs):
        with KongClient() as kc:
            resp = await kc.apis.get()
            installed_apis = await resp.json()
            installed_apis = [KongApi(**api) for api in installed_apis['data']]
            config_apis = [KongApi(**api) for api in config.get('apis', [])]
            docker_apis = await get_apis_from_docker()
            all_apis = set(config_apis) | set(docker_apis)

            to_install = all_apis - set(installed_apis)
            to_delete = []

            for api in installed_apis:
                if not api in all_apis:
                    to_delete.append(api)

            for api in to_install:
                await api.register()

            for api in to_delete:
                await api.unregister()
            return {'was': [a.to_dict() for a in installed_apis],
                    'installed': [a.to_dict() for a in to_install],
                    'deleted': [a.to_dict() for a in to_delete]}

        return False


CHECKERS = [Acting(), Plugins(), Consumers(), Apis()]

