# ecowitt2aprs

This Python package contains a script that queries the Ecowitt weather station data, transforming it into a Cumulus "[wxnow.txt](https://cumuluswiki.org/a/Wxnow.txt)" format which is printed to stdout.  

This script is intended to be used with the [Direwolf](https://github.com/wb2osz/direwolf) software AX.25 packet modem software for the purposes of relaying Ecowitt weather information via [Automatic Packet Reporting System (APRS)](https://en.wikipedia.org/wiki/Automatic_Packet_Reporting_System).

## Installation

`ecowitt2aprs` is best installed into a Python virtual environment.  For example

```bash
$ python -m venv /path/to/venv
$ . /path/to/venv/bin/activate
$ python -m pip install ecowitt2aprs
```

## Usage

`ecowitt2aprs` relies on authentication secrets provided in `config.yaml`.  Ecowitt API and App keys are required, along with the MAC address of the weather station used to capture the data.  These are inserted into `config.yaml` (see template in the repository), which should be given user read/write access only (i.e. Posix 600 octal code).  See the [Ecowitt API documentation](https://doc.ecowitt.net/web/#/apiv3en?page_id=11) for details.

```python
$ . /path/to/venv/bin/activate
$ ecowitt2aprs -c config.yaml

```
