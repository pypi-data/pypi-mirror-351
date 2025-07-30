"""Poll Ecowitt weather and return an APRS WX string"""

from argparse import ArgumentParser
from datetime import datetime, timedelta, UTC
import yaml
import urllib3 as urllib


__all__ = ["transform"]


def find(d, path):
    keys = path.split("/")
    rv = d
    for key in keys:
        rv = rv[key]

    return float(rv["value"])


class Ecowitt:
    def __init__(self, url, app_key, api_key, mac_addr):
        self.url = url
        self.auth_fields = {
            "application_key": app_key,
            "api_key": api_key,
            "mac": mac_addr,
        }

    def query_api(self, api_cmd, query_params):
        http = urllib.PoolManager()

        response = http.request(
            "GET",
            url=self.url + "/" + api_cmd,
            fields=self.auth_fields | query_params,
            timeout=4.0,
        )
        return response.json()

    def get_instant_data(self):
        content = self.query_api("real_time", {"call_back": "all"})

        wx = content["data"]

        return {
            "wind_direction": find(wx, "wind/wind_direction"),
            "wind_speed": find(wx, "wind/wind_speed"),
            "wind_gust": find(wx, "wind/wind_gust"),
            "temperature": find(wx, "outdoor/temperature"),
            "rain_hour": find(wx, "rainfall/hourly") * 100,
            "rain_today": find(wx, "rainfall/daily") * 100,
            "humidity": find(wx, "outdoor/humidity"),
            "abs_pressure": find(wx, "pressure/absolute") * 33.8639 * 10,
        }

    def get_history(self):
        now = datetime.now(UTC)
        yesterday = now - timedelta(days=1)

        content = self.query_api(
            "history",
            query_params={
                "start_date": yesterday.isoformat(),
                "end_date": now.isoformat(),
                "call_back": "rainfall",
                "cycle_type": "5min",
            },
        )

        rain_rate_in_per_hr = [
            float(x) for x in content["data"]["rainfall"]["rain_rate"]["list"].values()
        ]

        return {"rain_24h": sum(rain_rate_in_per_hr) / 12 * 100}


def ecowitt_to_aprs(data):
    float_data = [
        data["wind_direction"],
        data["wind_speed"],
        data["wind_gust"],
        data["temperature"],
        data["rain_hour"],
        data["rain_24h"],
        data["rain_today"],
        data["humidity"],
        data["abs_pressure"],
    ]

    aprs_str = "{:03.0f}/{:03.0f}g{:03.0f}t{:03.0f}r{:03.0f}p{:03.0f}P{:03.0f}h{:02.0f}b{:05.0f}"

    return aprs_str.format(*float_data)


def transform(url, app_key, api_key, mac_addr):
    """Transform Ecowitt-formated JSON to APRS Complete Weather Report

    Args:
      url: the Ecowitt API base URL
      app_key: the Ecowitt Application Key
      api_key: the Ecowitt API key
      mac_addr: MAC address of the local Ecowitt device

    Returns:
      Nothing.  The APRS-formatted string is printed to stdout.
    """

    ecowitt = Ecowitt(url, app_key, api_key, mac_addr)
    instant_data = ecowitt.get_instant_data()
    history = ecowitt.get_history()

    aprs_wx_str = ecowitt_to_aprs(instant_data | history)
    print(aprs_wx_str)


def parseargs():
    argparser = ArgumentParser()
    argparser.add_argument(
        "-c", "--config", type=str, required=True, help="path to configuration file"
    )

    return argparser.parse_args()


def main():
    args = parseargs()
    with open(args.config, "r") as f:
        config = yaml.safe_load(f)

    transform(
        config["ecowitt_url"],
        config["ecowitt_app_key"],
        config["ecowitt_api_key"],
        config["ecowitt_mac_addr"],
    )


if __name__ == "__main__":
    main()
