import codecs
import logging
from urllib import parse

from mopidy import httpclient
from mopidy_subsonic import Extension, __version__
import requests
from requests.exceptions import RequestException


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class SubsonicClient:
    def __init__(self, config):
        self.base_url = config["subsonic"]["base_url"]
        self.port = config["subsonic"]["port"]

        if not self.port:
            if self.base_url[:5] == "https":
                self.port = 443
            elif self.base_url[:4] == "http":
                self.port = 80
            else:
                raise Exception("Cannot determine port")

        proxy = httpclient.format_proxy(config["proxy"])
        full_user_agent = httpclient.format_user_agent(
            f"{Extension.dist_name}/{__version__}"
        )

        session = requests.Session()
        session.proxies.update({"http": proxy, "https": proxy})
        session.headers.update({"user-agent": full_user_agent})

        self.session = session

        p = codecs.encode(config["subsonic"]["password"].encode("ascii"), "hex").decode(
            "ascii"
        )
        params = (
            ("u", config["subsonic"]["username"]),
            ("p", f"enc:{p}"),
            ("v", "1.9.0"),
            ("c", Extension.dist_name),
            ("f", "json"),
        )

        self.session.params.update(params)
        response = self.do("ping")
        if response["status"] == "ok":
            logger.info("Subsonic auth success")

        self.params = params

    def do(self, endpoint, params=None):
        try:
            response = self.session.get(
                f"{self.base_url}/{endpoint}.view", params=params
            ).json()["subsonic-response"]
            assert (
                "error" not in response
            ), f"Subsonic error: {response['error']['message']}"
            return response
        except AssertionError as e:
            logger.error(e)
        except RequestException as e:
            logger.error(f"Subsonic error - connection failed: {e}")

    def get_stream_uri(self, uri):
        return f"{self.base_url}/stream.view?id={uri}&" + parse.urlencode(self.params)
