# logmatic-docker
*Link to the [Logmatic.io documentation](http://doc.logmatic.io/docs/docker)*

The Logmatic.io's container finds all your running containers' logs, events and stats and stream them to your platform.

# Use the image available on docker hub

This container as for unique option to pass the api key of your Logmatic.io's platform.

So to use the image available on docker hub simply run the following command:

```
docker run -dt -v /var/run/docker.sock:/var/run/docker.sock logmatic/logmatic-docker <your_api_key>
```

The mapping to the docker socket is really important as this is why we are able to identify all the running containers and follow their logs.

Nothing more to do.

# Options

Several options are allowed after the api key.

```
> logmatic-docker [apiKey]
   [-a ATTR (eg myattribute="my attribute")] //Several times ok
   [-h HOSTNAME (default "api.logmatic.io")] [-p PORT (default "10514")]
   [--namespace NAMESPACE (default "docker")]
   [--matchByImage REGEXP] [--matchByName REGEXP]
   [--skipByImage REGEXP] [--skipByName REGEXP]
   [--no-dockerEvents]
   [--no-stats] [-i SECONDS (default 30s)]
```


## Add extra attributes

You can add extra attributes to all the pushed entries by chaining the option "--attr" or "-a".

## Match / Skip by name or image

If you don't want all your containers to send log entries to Logmatic.io you can user the options `--matchByImage`, `--matchByName`, `--skipByImage` or `--skipByName`.

However, use one inclusion/exclusion policy as these options cannot live together.


## Disable docker container stats

You can disable container stats for each container using `--no-stats`. You can also set the interval with `-i statsInterval` (set to
30 seconds by default).

## Disable docker events

You can disable container events for each container using `--no-dockerEvents`

## Namespace the docker attributes

By default all the attributes related to Docker such as the container id, the name, the image etc... are contained into the `docker` object (as illustrated below). You can then use this parameter to change this namespace. With an empty namespace `--namespace ""`: all these attributes are merged at the root level.

# What are the data types sent to Logmatic.io?

This container sends 3 types of data:

- the log data published by your containers
- the docker events
- the docker stats

## Log data

The log data is published as is associated with some meta-data that identifies the container.
An NGINX log for instance would look like this:

```json
{
  "docker": {
    "image": "nginx",
    "id": "<container_id>",
    "name": "<container_name",
    "v": "<version>",
    "data_type": "log",
  },
  "message": "192.168.99.1 - - [15/Dec/2015:17:36:50 +0000] \"GET / HTTP/1.1\" 304 0 \"-\" \"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36\" \"-\""
}
```

**NOTE about JSON logging:**
If the container logs in JSON, the message field contains a valid JSON object. Logmatic.io will then parse it by default and you'll get all your attributes properly created at the root level in the user interface.

## Docker events

Docker events tells you the activity on your docker machine: create, kill, commit, etc...

```json
{
  "docker": {
    "image": "<image_name>",
    "id": "<container_id>",
    "name": "<container_name>",
    "host": "<your_host>",
    "type": "create",
    "data_type": "event"
  },
  "message": "[Docker event] host=\"a5900527eead577df14c7917e83f0b6ebeb7b3d103e44d0a93a1c05316c6d391\" name=\"boring_hypatia\" event=\"create\""
}
```

## Docker stats

Docker stats are all the metrics that matters by container. And there are a lot of them.

```json
{
  "docker": {
    "image": "<image_name>",
    "id": "<container_id>",
    "name": "<container_name>",
    "data_type": "stats",
    "stats": {
      "..."
    }
  },
  "message": "[Docker stats] host=\"nginx\" name=\"berserk_fermi\" main stats: [cpu%=0% mem%=0%]"
}
```

# Incoming features

We are at early stage concerning this docker instrumentation any comments are welcome and we will do as much as we can to integrate the desired features!
