import yaml


def load_config():
    loaded = {}
    try:
        with open('/config.yml') as f:
            loaded = yaml.load(f)
    except (IOError, OSError):
        pass
    return loaded

config = {
    'kong_admin_uri': 'http://kong:8001/'
}
config.update(load_config())
