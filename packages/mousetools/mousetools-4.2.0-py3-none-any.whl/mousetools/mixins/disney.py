import json
import logging

import httpx

from mousetools.auth import auth_obj

logger = logging.getLogger(__name__)


class DisneyAPIMixin:
    def get_disney_data(self, url: str):
        """
        Sends a request to the Disney API at the given url and returns the data.

        Args:
            url (str): API url to request data from.

        Returns:
            (dict): The disney data.

        Raises:
            (EntityIDNotFoundError): If the entity is not found.
            (httpx.HTTPError): All other errors during http request.
        """
        logger.info("Sending request to %s", url)
        response = httpx.get(url, headers=auth_obj.get_headers())
        logger.debug("Response status: %s", response.status_code)

        try:
            response.raise_for_status()
            data = response.json()
        except (httpx.HTTPError, json.decoder.JSONDecodeError) as err:
            logger.warning("Request failed. Error: %s", err)
            return None

        return data
