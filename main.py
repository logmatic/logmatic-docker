#!/usr/bin/python
import argparse
import logging
import sys
import threading
from time import sleep

import docker
import logmatic

from agent.AgentReporter import AgentReporter


internal_logger = logging.getLogger()

# Args parser settings
parser = argparse.ArgumentParser(prog="logmatic-docker", description='Send logs, events and stats to Logmatic.io')
parser.add_argument("token", metavar="LOGMATIC_API_KEY", help='The Logmatic.io API key')
parser.add_argument("--no-ssl", dest='ssl', action="store_false", help="Do not use ssl connection")
parser.add_argument('--no-logs', dest='logs', action="store_false", help="Disable the logs streams")
parser.add_argument('--no-stats', dest='stats', action="store_false", help="Disable the stats streams")
parser.add_argument('--no-detailed-stats', dest='detailed_stats', action="store_false", help="Disable stats streams")
parser.add_argument('--no-events', dest='events', action="store_false", help="Disable the event stream")
parser.add_argument("--namespace", dest='ns', help="Default namespace")
parser.add_argument("--hostname", dest='hostname', help="Logmatic.io's hostname (default api.logmatic.io)")
parser.add_argument("--port", dest='port', type=int, help="Logmatic.io's port (default 10514)")
parser.add_argument("--timeout", dest='timeout', type=int, help="Timeout")
parser.add_argument("--debug", dest="debug", action="store_true", help="Enable debugging")
parser.add_argument("-i", dest='interval', type=int, help="Seconds between to stats report (default 30)")
parser.add_argument("--attr", dest="attrs", action='append', help="eg my_attribute=\"my attribute\"")
parser.add_argument("--docker-version", dest='docker_version', metavar="VER", help="Force the Docker version to use")
parser.add_argument("--skipByImage", dest='skip_image', metavar="REGEX", help="Skip container by image name")
parser.add_argument("--skipByName", dest='skip_name', metavar="REGEX", help="Skip container by container name")
parser.add_argument("--matchByImage", dest='match_image', metavar="REGEX", help="Match container by image name")
parser.add_argument("--matchByName", dest='match_name', metavar="REGEX", help="Match container by container name")
parser.add_argument("--matchByLabel", dest='match_label', metavar="LABEL", help="Format either \"key\" or \"key=value\"")

# Default values
parser.set_defaults(logs=True)
parser.set_defaults(stats=True)
parser.set_defaults(detailed_stats=True)
parser.set_defaults(events=True)
parser.set_defaults(ns="docker")
parser.set_defaults(hostname="api.logmatic.io")
parser.set_defaults(port=10515)
parser.set_defaults(ssl=True)
parser.set_defaults(interval=30)
parser.set_defaults(attrs=[])
parser.set_defaults(debug=False)
parser.set_defaults(docker_version="auto")
parser.set_defaults(skip_name=None)
parser.set_defaults(skip_image=None)
parser.set_defaults(match_name=None)
parser.set_defaults(match_image=None)
parser.set_defaults(match_label=None)
parser.set_defaults(timeout=120)

args = parser.parse_args()

# Initialise the logger for Logmatic.io
logmatic_logger = logging.getLogger("docker-logmatic")
handler = logmatic.LogmaticHandler(args.token, host=args.hostname, port=args.port, ssl=args.ssl)
handler.setFormatter(logmatic.JsonFormatter(fmt="%(message)"))
logmatic_logger.addHandler(handler)
logmatic_logger.setLevel(logging.DEBUG)
logmatic_logger.propagate = False

if args.debug is True:
    internal_logger.setLevel(logging.DEBUG)
    sys_handler = logging.StreamHandler(sys.stderr)
    internal_logger.addHandler(sys_handler)
    internal_logger.debug(args)
else:
    internal_logger.disabled = True


# Initialise the connection to the local daemon
base_url = 'unix://var/run/docker.sock'
client = docker.DockerClient(base_url=base_url, timeout=args.timeout, version=args.docker_version)

# Main logic starts here
agent = AgentReporter(client=client, logger=logmatic_logger, args=args)
filters = None
if args.match_label:
    filters = {"label": args.match_label}

# Initialize all threads
event_thread = None
log_threads = {}
logs = False

# Main loop
while 1:

    try:
        containers = None
        # Start the event thread, and check if it's alive each seconds
        if args.events is True and (event_thread is None or not event_thread.isAlive()):
            internal_logger.info("Starting the event stream thread")
            event_thread = threading.Thread(target=agent.export_events)
            event_thread.daemon = True
            event_thread.start()

        # Start all log threads, and check if they're alive each x seconds
        if args.logs is True or args.stats is True:
            try:
                containers = client.containers.list(filters=filters)
            except Exception as e:
                internal_logger.exception("Unexpected error during the listing of the containers: {}".format(e))
            containers_filtered = agent.filter(containers)
            for container in containers_filtered:
                # Start threads and check if each logging thread are alive
                if args.logs is True and (container.id not in log_threads or not log_threads[container.id].isAlive()):
                    internal_logger.info("Starting the log stream thread for " + container.id)
                    log_threads[container.id] = threading.Thread(target=agent.export_logs, args=[container])
                    log_threads[container.id].daemon = True
                    log_threads[container.id].start()

                # Export stats to Logmatic.io
                if args.stats is True:
                    agent.export_stats(container, detailed=args.detailed_stats)

        internal_logger.debug("Next tick in {}s".format(args.interval))
        sleep(args.interval)

    except (KeyboardInterrupt, SystemExit):
        exit(0)
