import logging
import re

import requests
from docker.errors import DockerException

from agent.Calculator import Calculator

internal_logger = logging.getLogger()


class AgentReporter:
    def __init__(self, client, logger, args):
        self.client = client
        self.logger = logger
        self.args = args
        self.calculator = Calculator()
        self.local_cache = {}
        self.attrs = {}
        for attr in args.attrs:
            kv = attr.split("=")
            if len(kv) > 1:
                self.attrs[kv[0]] = kv[1]
            else:
                self.attrs[kv[0]] = ""

        internal_logger.info("Initialize a new agent reporter")
        self.daemon_name = self.client.info()["Name"]

    def export_events(self):
        try:
            events = self.client.events(decode=True)
            for event in events:
                if event["Type"] == "container":
                    container_meta = {
                        self.args.ns: {
                            "id": event["id"],
                            "daemon_name": self.daemon_name,
                            "image": event["Actor"]["Attributes"]["image"],
                            "name": event["Actor"]["Attributes"]["name"],
                            "status": event["status"],
                        },
                        "@marker": ["docker"]
                    }
                    if len(self.attrs):
                        container_meta["attr"] = self.attrs

                    # override if tehre are more info about the container
                    if event["id"] in self.local_cache:
                        container_meta = self.local_cache[event["id"]].copy()

                    container_meta["@marker"].append("docker-events")
                    container_meta[self.args.ns]["event"] = event["Action"]

                    # send it to Logmatic.io
                    self.logger.info("[Docker event] name:{} >> event:{} (image={})"
                                     .format(event["Actor"]["Attributes"]["name"],
                                             event["Action"],
                                             event["Actor"]["Attributes"]["image"]),
                                     extra=container_meta)

        except (requests.exceptions.ConnectionError, DockerException) as error:
            internal_logger.error("Unexpected end of event stream): {}".format(error))
        except Exception as e:
            internal_logger.error("Unexpected error: {}".format(str(e)))

    def export_stats(self, container, detailed):
        try:
            meta = self._build_context(container)
            meta["@marker"].append("docker-stats")
            stats = container.stats(stream=False, decode=True)
            computed_stats = self.calculator.compute_human_stats(container, stats)
            if detailed is True:
                meta[self.args.ns]["stats"] = stats
            else:
                meta[self.args.ns]["stats"] = {
                    "blkio_stats": {},
                    "memory_stats": {},
                    "cpu_stats": {},
                    "networks": {}
                }

            meta[self.args.ns]["stats"]["blkio_stats"].update(computed_stats["blkio_stats"])
            meta[self.args.ns]["stats"]["memory_stats"].update(computed_stats["memory_stats"])
            meta[self.args.ns]["stats"]["cpu_stats"].update(computed_stats["cpu_stats"])
            for interface in computed_stats["networks"]:
                if interface not in meta[self.args.ns]["stats"]["networks"]:
                    meta[self.args.ns]["stats"]["networks"][interface] = {}
                meta[self.args.ns]["stats"]["networks"][interface].update(computed_stats["networks"][interface])

            message = ""
            if "error" not in computed_stats["cpu_stats"]:
                message += " cpu:{:.2f}%".format(computed_stats["cpu_stats"]["total_usage_pct"] * 100.0)
            if "error" not in computed_stats["memory_stats"]:
                message += " mem:{:.2f}%".format(computed_stats["memory_stats"]["usage_pct"] * 100.0)
            if "error" not in computed_stats["blkio_stats"]:
                message += " io:{:.2f}MB/s".format(computed_stats["blkio_stats"]["total_bps"] / 1000000.0)
            if "error" not in computed_stats["networks"]:
                message += " net:{:.2f}MB/s".format(
                    (computed_stats["networks"]["all"]["tx_bytes_ps"] + computed_stats["networks"]["all"][
                        "rx_bytes_ps"]) / 1000000.0)

            self.logger.info(
                "[Docker stats] name:{} >> {} (host:{} image:{})".format(meta[self.args.ns]["name"], message,
                                                                         meta[self.args.ns]["hostname"],
                                                                         meta[self.args.ns]["image"]), extra=meta)

        except (requests.exceptions.ConnectionError, DockerException) as error:
            internal_logger.error("Unexpected end of stats stream for container({}): {}"
                                  .format(container.short_id, error))
        except Exception as e:
            internal_logger.error("Unexpected error: {}".format(str(e)))

    def export_logs(self, container):
        """Send all logs to Logmatic.io"""
        if container.attrs["Config"]["Image"].startswith("logmatic/logmatic-docker"):
            return
        try:
            line = ""
            meta = self._build_context(container)
            meta["@marker"].append("docker-logs")
            logs = container.logs(stream=True, follow=True, stdout=True, stderr=False, tail=0)
            for chunk in logs:
                # Append all char into a string until a \n
                if chunk is not '\n':
                    line = line + chunk
                else:
                    self.logger.info(line, extra=meta)
                    line = ""

        except (requests.exceptions.ConnectionError, DockerException) as error:
            internal_logger.error(
                "Unexpected end of logs stream for container({}): {}".format(container.short_id, error))
        except Exception as e:
            internal_logger.error("Unexpected error: {}".format(str(e)))

    def _build_context(self, container):
        """Internal method, to build the container context"""
        try:
            labels = {
                "all": [],

            }
            for label in container.attrs["Config"]["Labels"]:
                labels["all"].append(label)
                if container.attrs["Config"]["Labels"][label] != "":
                    labels[label] = container.attrs["Config"]["Labels"][label]

            meta = {
                self.args.ns: {
                    "id": container.id,
                    "short_id": container.short_id,
                    "name": container.name,
                    "status": container.status,
                    "daemon_name": self.daemon_name,
                    "labels": labels,
                    "hostname": container.attrs["Config"]["Hostname"],
                    "image": container.attrs["Config"]["Image"],
                    "created": container.attrs["Created"],
                    "pid": container.attrs["State"]["Pid"]
                },
                "@marker": ["docker"],
                "severity": "INFO"
            }

            if len(self.attrs):
                meta["attr"] = self.attrs

            self.local_cache[container.id] = meta.copy()
            return meta

        except Exception as e:
            internal_logger.error("Unexpected error: {}".format(str(e)))

    def filter(self, containers):
        filtered = []

        # Continue if no filter has been set
        if not (self.args.skip_name or self.args.skip_image or self.args.match_name or self.args.match_image):
            internal_logger.debug("Not filter has been set")
            return containers

        for c in containers:
            internal_logger.debug("Checking filter on {}/{}".format(c.name, c.short_id))
            # skip container by image name
            if self.args.skip_image and re.search(self.args.skip_image, c.attrs["Config"]["Image"]):
                continue
            # skip container by container name
            if self.args.skip_name and re.search(self.args.skip_name, c.name):
                continue
            # match container by image name
            if self.args.match_image and not re.search(self.args.match_image, c.attrs["Config"]["Image"]):
                continue
            # match container by name name
            if self.args.match_name and not re.search(self.args.match_name, c.name):
                continue

            filtered.append(c)

        internal_logger.debug("Watched containers: {}".format(filtered))
        return filtered
