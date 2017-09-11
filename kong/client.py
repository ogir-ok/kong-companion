import urllib
import aiohttp
from functools import partial

from config import config

class KongClient:
    """
    Wrapper for kong operations
    """

    def __init__(self, path=None, session=None):
        self._path = []
        if path:
            self._path = path

        if session:
            self._session = session

    def __getattr__(self, item):

        if item in ['get', 'post', 'put', 'patch', 'delete']:
            return partial(self._perform, item)

        return self.url(item)

    def __enter__(self, *a, **kwa):
        self._session = aiohttp.ClientSession(*a, **kwa)
        return self

    def __exit__(self, *a, **kwa):
        self._session.close()

    def _url(self):
        return '/'.join(self._path)

    def _perform(self, method, *a, **kwa):
        url = urllib.parse.urljoin(config['kong_admin_uri'], self._url())
        return getattr(self._session, method)(url, *a, **kwa)

    def __call__(self, *a, **kwa):
        return self.get(*a, **kwa)

    def url(self, item):
        """
        Add url param (like client.bar.url(param).qq = http://api.foo/bar/{param}/qq/)
        """
        return self.__class__(path=[*self._path, item], session=self._session)


