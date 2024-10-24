import hashlib

import requests
from loguru import logger


class KeeneticClient:
    def __init__(
        self,
        url: str,
        username: str,
        password: str,
    ):
        if not url.endswith("/"):
            url += "/"

        self._auth_endpoint = f"{url}auth"
        self._rci_endpoint = f"{url}rci/"
        self._ci_endpoint = f"{url}ci/"

        self.username = username
        self.password = password

    def auth(self):
        logger.info("Authenticating")

        session = requests.session()
        res = session.get(self._auth_endpoint)

        device = res.headers["X-NDM-Realm"]
        token = res.headers["X-NDM-Challenge"]

        digits = f"{self.username}:{device}:{self.password}"
        digits = hashlib.md5(digits.encode("utf-8")).hexdigest()
        digits = f"{token}{digits}"
        digits = hashlib.sha256(digits.encode("utf-8")).hexdigest()

        res = session.post(
            url=self._auth_endpoint,
            json={"login": self.username, "password": digits},
        )
        res.raise_for_status()
        logger.success("Authentication successful")

        self.session = session

    def startup_config(self) -> tuple[str, str]:
        res = self.session.get(self._ci_endpoint + "startup-config.txt")
        res.raise_for_status()
        return (
            res.headers["Content-Disposition"].split("filename=")[-1].strip('"'),
            res.content.decode(),
        )
