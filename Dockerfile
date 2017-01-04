FROM python:3.5.2-alpine

# Update
RUN apk add --update python py-pip
RUN pip install logmatic-python && \
    pip install docker

VOLUME [ "/var/run/docker.sock" ]
ADD /agent /app/agent

ADD main.py /app/

ENTRYPOINT ["python",  "/app/main.py"]