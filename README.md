# Kong Companion

> kong-companion sets up container that manages kong(http://getkong.org/) and creates APIs based on `labels` in docker containers

# Quickstart

## Example of `config.yml`

```
#URI of kong admin api
kong_admin_uri: http://kong:8001/

# list of plugins with configs that should be installed
plugins:
  - name: jwt
    config.claims_to_verify: exp
    config.anonymous: 4d924084-1adb-40a5-c042-63b19db421d1

# list of consumers to create
consumers:
  - id: 4d924084-1adb-40a5-c042-63b19db421d1
    username: anonymous
    custom_id: anonymous

# list of default manual-created apis
apis:
  - name: root-fallback
    uris: /
    upstream_url: 'https://fallback.com/'
  - name: foo1
  	 uris: /foo/
  	 upstream_url: 'http://foo.com'
  - name: foo2
  	 hosts: foo.atomcream.com 
  	 upstream_url: 'http://foo.com'

     
```

## Example of `docker-compose.yml`

```
version: '2.1'

services:
  db:
    image: postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: kong
      POSTGRES_DB: kong

  kong:
    image: kong
    restart: unless-stopped
    environment:
      KONG_PROXY_LISTEN: 0.0.0.0:80
      KONG_DATABASE: postgres
      KONG_PG_HOST: db
      KONG_LOG_LEVEL: debug
    ports:
      - 80:80

  kong-companion:
    image: atomcream/kong-companion
    restart: unless-stopped
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./config.yml:/web/config.yml
    labels:
      kong.uris: /companion/ # all calls to /companion will be routed to this containers
      kong.hosts: companion.atomcream.com # all calls with host companion.atomcream.com will be routed here too

  dashboard:
    image: pgbi/kong-dashboard
    restart: unless-stopped
    labels:
      kong.uris: /dashboard/ 
      kong.port: '8080' # port which container is listening
      
networks:
  default:
    external:
      name: kong-local
```

