from typing import Optional, Union

from mousetools.auth import auth_obj
from mousetools.channels.enums import DLRCouchbaseChannels, WDWCouchbaseChannels
from mousetools.enums import DestinationShort
from mousetools.mixins.disney import DisneyAPIMixin


class Search(DisneyAPIMixin):
    _search_service_base = auth_obj._environments["searchServiceUrl"]

    def __init__(self, destination: Union[DestinationShort, str]):
        """
        Args:
            destination (Union[DestinationShort, str]): Search the facilities for this destination
        """
        if isinstance(destination, DestinationShort):
            destination = destination.value
        self.destination = destination
        self._facilities_channel = (
            WDWCouchbaseChannels.FACILITIES.value
            if destination == DestinationShort.WALT_DISNEY_WORLD
            else DLRCouchbaseChannels.FACILITIES.value
        )

    def search(self, query: str, max_results: int = 10) -> Optional[list[dict]]:
        """Send a request to the search service

        Args:
            query (str): Search query
            max_results (int, optional): Maximum number of results to return in the list. Defaults to 10.

        Returns:
            (Optional[list[dict]]): List of results
        """
        api_data = self.get_disney_data(
            f"{self._search_service_base}/mobileapi/v1/entities/search?q={query}&brand={self.destination}"
        )
        our_results = []
        for i in api_data.get("results", [])[:max_results]:
            tmp = {}
            tmp["entity_id"] = i["id"]
            tmp["name"] = i["title"][0]
            tmp["search_score"] = i["score"]
            tmp["channel_id"] = f"{self._facilities_channel}.{i['id'].rsplit('=')[-1].lower()}.{i['id']}"
            our_results.append(tmp)
        return our_results

    def __call__(self, *args, **kwargs) -> Optional[list[dict]]:
        """Call the search function

        Returns:
            (Optional[list[dict]]): List of results
        """
        return self.search(*args, **kwargs)

    def __repr__(self):
        return f"Search(destination='{self.destination}')"
