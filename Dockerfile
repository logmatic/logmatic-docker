FROM alpine:latest
MAINTAINER Logmatic.io <support@logmatic.io>

# Install nodejs
RUN apk -U add nodejs && \
    mkdir -p /usr/src/app

WORKDIR /usr/src/app
ADD package.json /usr/src/app/

# Install the app
RUN npm install
ADD index.js /usr/src/app

ENTRYPOINT ["/usr/src/app/index.js"]
