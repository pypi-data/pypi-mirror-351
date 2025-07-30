import json
import logging
import re
import typing

import httpx

from mousetools.auth import auth_obj

logger = logging.getLogger(__name__)


class CouchbaseMixin:
    _couchbase_url = "https://" + auth_obj._environments["syncGatewayUrl"].split("//")[1]
    _headers: dict = auth_obj.get_couchbase_headers()

    def get_channel_data(self, channel_name: str) -> typing.Union[dict, None]:
        """
        Sends a request to the Disney Couchbase API with the given channel ID and returns the data.

        Args:
            channel_name (str): Couchbase channel to request data from.

        Returns:
            (dict): The disney data.

        Raises:
            (httpx.HTTPError): All errors during http request.
        """

        payload = {
            "docs": [
                {"id": channel_name},
            ],
            "json": True,
        }

        response = httpx.post(self._couchbase_url + "/_bulk_get", json=payload, headers=self._headers)
        logger.debug("Response status: %s", response.status_code)
        data = None
        try:
            response.raise_for_status()
            raw_data = response.text

            cont_reg = re.compile(r"\w+-\w+:\s\w+\/\w+")
            raw_data = re.sub(cont_reg, "", raw_data)
            raw_data = raw_data.splitlines()

            for line in raw_data:
                if line != "" and line[0] != "-":
                    try:
                        data = json.loads(line)
                    except Exception:
                        logger.debug("Failed to parse line: %s", line)
                        continue
        except httpx.HTTPError as err:
            logger.error("Request failed: %s", err)
            return None

        return data

    def get_channel_changes(self, channel_name: str, since: typing.Union[int, None] = None) -> typing.Union[dict, None]:
        try:
            payload = {
                "channels": channel_name,
                "style": "all_docs",
                "filter": "sync_gateway/bychannel",
                "feed": "normal",
                "heartbeat": 30000,
            }
            if since:
                payload["since"] = since

            response = httpx.post(self._couchbase_url + "/_changes", json=payload, headers=self._headers)
            data = response.raise_for_status().json()
        except httpx.HTTPError as err:
            logger.error("Request failed: %s", err)
            return None

        return data
