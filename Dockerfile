FROM python:3
MAINTAINER Ihor Harahatyi <i.harahatyi@atomcream.com>

ADD . /web
WORKDIR /web

RUN pip install -r requirements.txt

EXPOSE 80

HEALTHCHECK --interval=5s --timeout=15s --retries=10 \
    CMD curl -f http://localhost/

CMD /bin/bash -c "cd /web/ && python main.py"
