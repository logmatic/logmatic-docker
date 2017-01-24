# logmatic-docker
*Link to the [Logmatic.io documentation](http://doc.logmatic.io/docs/docker)*

The Logmatic.io's container finds all your running containers' logs, events and stats and stream them to your platform.

# Use the image available on docker hub

This container as for unique option to pass the api key of your Logmatic.io's platform.

So to use the image available on docker hub simply run the following command:

```
docker run -d -v /var/run/docker.sock:/var/run/docker.sock logmatic/logmatic-docker <your_api_key>
```

The mapping to the docker socket is really important as this is why we are able to identify all the running containers and follow their logs.

Nothing more to do.

# Options

Several options are allowed after the api key.

```
> usage: logmatic-docker [-h] [--no-ssl] [--logs] [--no-logs] [--stats] [--no-stats]
                 [--no-detailed-stats] [--events] [--no-events] [--namespace NS]
                 [--hostname HOSTNAME] [--port PORT] [--debug] [-i INTERVAL]
                 [--attr ATTRS] [--docker-version VER] [--skipByImage REGEX]
                 [--skipByName REGEX] [--matchByImage REGEX]
                 [--matchByName REGEX] [--matchByLabel LABEL]
                 LOGMATIC_API_KEY
  
  Send logs, events and stats to Logmatic.io
  
  positional arguments:
    LOGMATIC_API_KEY      The Logmatic.io API key
  
  optional arguments:
    -h, --help            show this help message and exit
    --logs                Enable the logs streams
    --no-logs             Disable the logs streams
    --stats               Enable the stats streams
    --no-stats            Disable the stats streams
    --no-detailed-stats   Disable stats streams
    --events              Enable the event stream
    --no-events           Disable the event stream
    --namespace NS        Default namespace
    --hostname HOSTNAME   Logmatic.io's hostname (default api.logmatic.io)
    --port PORT           Logmatic.io's port (default 10514)
    --debug               Enable debugging
    -i INTERVAL           Seconds between to stats report (default 30)
    --attr ATTRS          eg myattribute="my attribute"
    --docker-version VER  Force the Docker version to use
    --skipByImage REGEX   Skip container by image name
    --skipByName REGEX    Skip container by container name
    --matchByImage REGEX  Match container by image name
    --matchByName REGEX   Match container by container name
    --matchByLabel LABEL  Format either "key" or "key=value"
```


## Add extra attributes

You can add extra attributes to all the pushed entries by chaining the option "--attr" or "-a".

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
      "image": "agileek/cpuset-test",
      "hostname": "f307d28f60f4",
      "daemon_name": "jarvis",
      "created": "2016-12-21T15:04:27.6401807Z",
      "name": "small_mahavira",
      "id": "f307d28f60f4695e90bd108b3a3bbb6c9fbd4e896187966515b9d18d104f1730",
      "short_id": "f307d28f60",
      "status": "running",
      "pid": 7931
    }
}
```

**NOTE about JSON logging:**
If the container logs in JSON, the message field contains a valid JSON object. Logmatic.io will then parse it by default and you'll get all your attributes properly created at the root level in the user interface.

## Docker events

Docker events tells you the activity on your docker machine: create, kill, commit, etc...

```json
{
    "message": "[Docker event] name:distracted_archimedes >> event:attach (image=ubuntu)",
    "docker": {
      "image": "ubuntu",
      "daemon_name": "jarvis",
      "name": "distracted_archimedes",
      "id": "65254830bfa3604f487d1603d509d45886f37f83412c4b18f809d148c5f60c4c",
      "event": "attach",
      "status": "attach"
    }
}
```

## Docker stats

Docker stats are all the metrics that matters by container. And there are a lot of them.

```json
{
    "message": "[Docker stats] name:small_mahavira >>  cpu:199.59% mem:0.01% io:0.00MB/s net:0.00MB/s (host:f307d28f60f4 image:agileek/cpuset-test)",

    "docker": {
        "image": "agileek/cpuset-test",
        "hostname": "f307d28f60f4",
        "created": "2016-12-21T15:04:27.6401807Z",
        "daemon_name": "jarvis",
        "name": "small_mahavira",
        "short_id": "f307d28f60",
        "status": "running",
        "pid": 7931,
        "id": "f307d28f60f4695e90bd108b3a3bbb6c9fbd4e896187966515b9d18d104f1730",
        "human_stats": { 
          //computed stats, display as percent or MB/s
        },
        "stats": {
          //raw stats,from the docker daemon
        }
  }
}
```

# Incoming features

We are at early stage concerning this docker instrumentation any comments are welcome and we will do as much as we can to integrate the desired features!
