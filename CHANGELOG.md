# v2.0

Refactoring in order to use the official Docker Client Library (docker-py)
Features:

* Labels are now reported to each event in the field `custom.docker.labels` 
* New optsion `--matchByLabel` to filter container stats and logs based on labels
* Add a subsection `human_stats` to each "stats event" to provide more clarity


Human stats example:
```json
{
  "human_stats": {
    "cpu_stats": {
      "total_usage_%": 0,
      "usage_in_kernelmode_%": 0,
      "per_cpu_usage_%": [
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0
      ],
      "usage_in_usermode_%": 0
    },
    "networks": {
      "all": {
        "rx_bytes_ps": 0,
        "tx_bytes_ps": 0,
        "tx_packets_ps": 0,
        "rx_dropped_ps": 0,
        "tx_dropped_ps": 0,
        "tx_errors_ps": 0,
        "rx_errors_ps": 0,
        "rx_packets_ps": 0
      },
      "eth0": {
        "tx_packets_ps": 0,
        "rx_dropped_ps": 0,
        "rx_bytes_ps": 0,
        "tx_dropped_ps": 0,
        "tx_errors_ps": 0,
        "rx_errors_ps": 0,
        "tx_bytes_ps": 0,
        "rx_packets_ps": 0
      }
    },
    "memory_stats": {
      "usage_%": 0.0003174765431030924
    },
    "blkio_stats": {
      "read_bps": 0,
      "write_bps": 0,
      "total_bps": 0,
      "total_iops": 0,
      "write_iops": 0,
      "read_iops": 0
    }
  }
}
```
# Migrating from v1.0 to v2.0
The v2.0 is based on the official docker client python library.
If, you are currently using the v1.0, here are the breaking changes:

* Replace `--no-dockerEvents` option by `--no-events`
* Replace the `--dockerEvents` option by `--events`
* Replace `-h` by `--hostname`, `-h` is now displaying the help
* Replace `-a` by `--attr`, `-a` is no longer supported

The content of each event has also evolved.

The field `custom.docker.data_type` is no longer supported and is replaced 
by `custom.@marker`. Use this new field instead the previous one.

