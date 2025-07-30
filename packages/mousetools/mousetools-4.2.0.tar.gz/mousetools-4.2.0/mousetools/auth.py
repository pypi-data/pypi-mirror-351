import base64
import json
import typing
from datetime import datetime, timedelta
from importlib.resources import as_file, files

import httpx
from Crypto.Cipher import AES


class Authentication:
    def __init__(self):
        self.time_of_expire: typing.Optional[datetime] = None
        self.access_token: typing.Optional[str] = None
        self._environments = self._decrypt_file("resources/environments.bin").get("production", {})

    def authenticate(self) -> tuple[str, int]:
        """Gets an access token from Disney and the token's expiration time

        Returns:
            (tuple[str, int]): Access token to the api and how long until it expires
        """

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "max-age=0",
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "Connection": "keep-alive",
            "Proxy-Connection": "keep-alive",
            "Accept-Encoding": "gzip, deflate",
        }

        body = {
            "grant_type": "assertion",
            "assertion_type": "public",
            "client_id": self._environments["authzClientId"],
        }

        response = httpx.post(
            f"{self._environments['authzServiceUrl']}/token",
            headers=headers,
            params=body,
            timeout=10,
        )
        response.raise_for_status()
        auth = response.json()

        return auth["access_token"], int(auth["expires_in"])

    def get_headers(self) -> dict[str, str]:
        """Creates the headers to send during the request

        Returns:
            (dict[str, str]): Headers for the request
        """

        if self.time_of_expire is None or (datetime.now() > self.time_of_expire):
            access_token, expires_in = self.authenticate()
            self.time_of_expire = datetime.now() + timedelta(seconds=(expires_in - 10))
            self.access_token = access_token

        headers = {
            "Authorization": f"BEARER {self.access_token}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "Accept": "*/*",
        }

        return headers

    def get_couchbase_headers(self) -> dict[str, str]:
        """Creates the headers to send during the couchbase request

        Returns:
            (dict[str, str]): Headers for the couchbase request
        """
        username = self._environments["syncGatewayUser"]
        password = self._environments["syncGatewayPass"]
        token = base64.b64encode(f"{username}:{password}".encode()).decode()

        header = {
            "Authorization": f"Basic {token}",
            "User-Agent": "CouchbaseLite/3.2.1-9 (Java; Android 16; sdk_gphone64_x86_64) EE/release, Commit/2109502be2@02fbcb1b8b44 Core/3.2.1 (19)",
            "Content-Type": "application/json",
            "Accept": "multipart/related",
        }

        return header

    def _decrypt_file(self, filename: str) -> dict:
        cipher = AES.new(self._e(), AES.MODE_GCM, nonce=self._b())
        with as_file(files("mousetools") / filename) as f, open(f, "rb") as file:
            decrypted = cipher.decrypt(file.read())
            return json.loads(decrypted.decode("Windows-1252")[:-16])

    def _e(self):
        s = ""
        for i in range(1, 17):
            if i % 2 != 0 or i >= 16:
                s += chr(i + 65)
            else:
                s += str(3.141592653589793)[i]
        bytes_ = s.encode("utf-8")
        return bytes_

    def _b(self):
        return bytes(reversed(self._e()))


auth_obj = Authentication()
