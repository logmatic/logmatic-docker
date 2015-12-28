# logmatic-docker
The Logmatic.io's container finds all your running containers' logs and stream it to your platform

# Use the image available on docker hub

This container as for unique option to pass the api key of your Logmatic.io's platform.

So to use the image available on docker hub simply run the following command:

```
docker run -v /var/run/docker.sock:/var/run/docker.sock logmatic/logmatic-docker <your_api_key>
```

The mapping to the docker socket is really important as this is why we are able to identify all the running containers and follow their logs.

Nothing more to do.

# Options

Several options are allowed after the api key.

```
> logmatic-docker [apiKey]
   [-a ATTR (eg myattribute="my attribute")]
   [-h HOSTNAME (default "api.logmatic.io")] [-p PORT (default "10514")]
   [--matchByImage REGEXP] [--matchByName REGEXP]
   [--skipByImage REGEXP] [--skipByName REGEXP]
```

## Add extra attributes

You can add extra attributes to all the pushed entries by chaining the option "--attr" or "-a".

## Match / Skip by name or image

If you don't want all your containers to send log entries to Logmatic.io you can user the options `--matchByImage`, `--matchByName`, `--skipByImage` or `--skipByName`.

However, use one inclusion/exclusion policy as these options cannot live together.

# What are the data sent to Logmatic.io?

This container sends 2 things:

- the log data published by your containers
- and the docker events

## The log data

The log data is published as is associated with some meta-data that identifies the container.
An NGINX log for instance would look like this:

```json
{
  "image": "nginx",
  "id": "<container_id>",
  "name": "<container_name",
  "v": "<version>",
  "message": "192.168.99.1 - - [15/Dec/2015:17:36:50 +0000] \"GET / HTTP/1.1\" 304 0 \"-\" \"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36\" \"-\""
}
```

## The docker events

Docker events tells you the activity on your docker machine: create, kill, commit, etc...

```json
{
  "image": "<image_name>",
  "id": "<container_id>",
  "name": "<container_name>",
  "host": "<your_host>",
  "type": "create",
  "message": "[Docker event] host=\"a5900527eead577df14c7917e83f0b6ebeb7b3d103e44d0a93a1c05316c6d391\" name=\"boring_hypatia\" event=\"create\""
}
```

# Incoming features

We are at early stage concerning this docker instrumentation any comments are welcome and we will do as much as we can to integrate the desired features!
