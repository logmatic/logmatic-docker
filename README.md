# logmatic/logmatic-docker

The logmatic-docker container finds all your running containers' logs, events and stats from all the running containers in the docker machine and streams it straight to your Logmatic.io's platform.
Want help or try Logmatic.io?:
 * Our documentation: [the Logmatic.io documentation page](http://doc.logmatic.io/docs/docker)
 * Our support team: [support@logmatic.io](mailto:support@logmatic.io)
 * Our website: [https://logmatic.io](https://logmatic.io)

## Releases and tags

* `1.2`, `1.2.2`, `latest`: The official Logmatic.io image
* `1.0` (*deprecated*): NodeJS docker client, not compatible with the Logmatic.io integration
* `dev`: dev-build from the github repository

The Logmatic.io's container finds all your running containers' logs, events and stats and stream them to your platform.



## Use the image available on docker hub

This container as for unique option to pass the api key of your Logmatic.io's platform.

So to use the image available on docker hub simply run the following command:

```
docker run -dt --name logmatic.io -v /var/run/docker.sock:/var/run/docker.sock:ro logmatic/logmatic-docker:1.2 <YOUR_API_KEY>
```

The mapping to the docker socket is really important as this is why we are able to identify all the running containers and follow their logs.

Nothing more to do.

# Options

Several options are allowed after the api key.

```
> usage: logmatic-docker [-h] [--no-ssl] [--no-logs] [--no-stats]
                 [--no-detailed-stats] [--no-events] [--namespace NAMESPACE]
                 [--hostname HOSTNAME] [--port PORT] [--debug] [-i INTERVAL]
                 [--attr ATTRS] [--docker-version DAEMON_VERSION] [--skipByImage REGEX]
                 [--skipByName REGEX] [--matchByImage REGEX]
                 [--matchByName REGEX] [--matchByLabel LABEL]
                 LOGMATIC_API_KEY
  
  Send logs, events and stats to Logmatic.io
  
  positional arguments:
    LOGMATIC_API_KEY      The Logmatic.io API key
  
  optional arguments:
    -h, --help            show this help message and exit
    --no-logs             Disable the logs streams
    --no-stats            Disable the stats streams
    --no-detailed-stats   Disable stats streams
    --no-events           Disable the event stream
    --namespace NAMESPACE        Default namespace
    --hostname HOSTNAME   Logmatic.io's hostname (default api.logmatic.io)
    --port PORT           Logmatic.io's port (default 10514)
    --timeout SEC         Set the timeout for docker client calls
    --debug               Enable debugging
    -i INTERVAL           Seconds between to stats report (default 30)
    --attr ATTRS          eg myattribute="my attribute"
    --docker-version DAEMON_VERSION  Force the Docker version to use
    --skipByImage REGEX   Skip container by image name
    --skipByName REGEX    Skip container by container name
    --matchByImage REGEX  Match container by image name
    --matchByName REGEX   Match container by container name
    --matchByLabel LABEL  Format either "key" or "key=value"
```


## Add extra attributes

You can add extra attributes to all the pushed entries by chaining the option "--attr" or "-a".
But, the good practice is to use container's labels instead.

## Match / Skip by name, image or label

If you don't want all your containers to send log entries to Logmatic.io you can user the options
`--matchByLabel`, `--matchByImage`, `--matchByName`, `--skipByImage` or `--skipByName`.

However, use one inclusion/exclusion policy as these options cannot live together.


## Disable docker container stats

You can disable container stats for each container using `--no-stats` or `--no-detailed-stats` if you want to keep only the
a summary of the usage. You can also set the interval with `-i INTERVAL` (set to
30 seconds by default).


## Disable docker events

You can disable container events for each container using `--no-events`

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
    "message": "192.168.99.1 - - [15/Dec/2015:17:36:50 +0000] \"GET / HTTP/1.1\" 304 0 \"-\" \"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36\" \"-\"",
    "docker": {
        "image": "agileek/logmatic-docker:latest",
        "daemon_name": "jarvis",
        "name": "grave_goldwasser",
        "id": "47cb6e825ac07e56d6e7ed9ae82e1b7438a1850150013c3aff30eeecd0d86939",
        "status": "running",
        "hostname": "47cb6e825ac0",
        "created": "2017-02-10T08:21:11.308113714Z",
        "pid": 4505,
        "short_id": "47cb6e825a"
    },
    "severity": "INFO",
    "timestamp": "2017-02-10T08:21:14.258Z"
}
```

**NOTE about JSON logging:**

If the container logs in JSON, the message field contains a valid JSON object. Logmatic.io will then parse it by default and you'll get all your attributes properly created at the root level in the user interface.

## Docker events

Docker events tells you the activity on your docker machine: create, kill, commit, etc...

```json
{
    "message": "[Docker event] name:amazing_engelbart >> event:start (image=chentex/random-logger)",
    "docker": {
        "image": "chentex/random-logger",
        "daemon_name": "jarvis",
        "name": "amazing_engelbart",
        "id": "fa755a06afb40f5e9657aaa4ed45e735b21826a5faee2737ce6ce0388b910d72",
        "event": "start",
        "status": "start",
        "hostname": "fa755a06afb4",
        "created": "2017-02-10T08:24:45.868923429Z",
        "pid": 5213,
        "short_id": "fa755a06af"
    },
    "severity": "INFO",
    "timestamp": "2017-02-10T08:24:47.044Z"
}
```

## Docker stats

Docker stats are all the metrics that matters by container. And there are a lot of them.

```json
{
    "message": "[Docker stats] name:grave_goldwasser >>  cpu:0.11% mem:0.21% io:0.00MB/s net:0.00MB/s (host:47cb6e825ac0 image:logmatic/logmatic-docker:latest)",
    "docker": {
        "image": "logmatic/logmatic-docker:latest",
        "daemon_name": "jarvis",
        "name": "grave_goldwasser",
        "id": "47cb6e825ac07e56d6e7ed9ae82e1b7438a1850150013c3aff30eeecd0d86939",
        "status": "running",
        "hostname": "47cb6e825ac0",
        "created": "2017-02-10T08:21:11.308113714Z",
        "pid": 4505,
        "short_id": "47cb6e825a",
        "stats": {
          //raw stats and computed,from the docker daemon
        }
    },
    "severity": "INFO",
    "timestamp": "2017-02-10T08:26:42.255Z"
}
```

# Incoming features

We are at early stage concerning this docker instrumentation any comments are welcome and we will do as much as we can to integrate the desired features!
