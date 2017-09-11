import aiodocker
from .client import KongClient


class KongApi:
    """
    Kong's api object
    """

    def __init__(self, name, uris=None, hosts=None, upstream_url=None, id=None, **kwa):
        self.id = id
        self.name = name
        self.uris = uris
        self.hosts = hosts
        self.upstream_url = upstream_url

    def __str__(self):
        return '<{} -> {}>'.format(self.uris if self.uris else self.hosts, self.upstream_url)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        return self.name != other.name

    def __hash__(self):
        return hash(self.name)

    async def register(self):
        data = {
            'name': self.name,
            'upstream_url': self.upstream_url,
            'hosts': self.hosts,
            'uris': self.uris
        }

        with KongClient() as kc:
            resp = await kc.apis.post(json=data)
            return await resp.json()

    async def unregister(self):
        if not self.id:
            raise ValueError('can not unregister api without id')

        with KongClient() as kc:
            resp = await kc.apis.url(self.id).delete()
            return await resp.json()

    def to_dict(self):
        return {
            'name': self.name,
            'upstream_url': self.upstream_url,
            'hosts': self.hosts,
            'uris': self.uris
        }


async def get_apis_from_container(container):
    """
    Will return one or two apis from docker container
    """
    apis = []
    name = container['Names'][0].replace('/', '')
    labels = container['Labels']

    if name and ('kong.uris' in labels or 'kong.hosts' in labels):
        uris = labels.get('kong.uris')
        hosts = labels.get('kong.hosts')
        port = labels.get('kong.port', '80')

        upstream = 'http://{}:{}/'.format(name, port)

        if uris:
            apis.append(KongApi(name, uris=uris, upstream_url=upstream))
        if hosts:
            apis.append(KongApi(name + '_uri', uris=uris, upstream_url=upstream))

    return apis


async def get_apis_from_docker():
    """
    Get all docker-based APIs
    """

    apis =[]

    docker = aiodocker.Docker()
    containers = await docker.containers.list()

    for c in containers:
        apis.extend(await get_apis_from_container(c._container))

    return apis


async def get_current_apis():
    """
    Get currently registered APIs
    """
    apis = []

    with KongClient() as kc:
        resp = await kc.apis.get()
        registered = await resp.json()
        for api in registered['data']:
            apis.append(KongApi(**api))

    return apis
