import logging
import typing
from datetime import datetime, timedelta
from enum import Enum

from dateutil.parser import isoparse

from mousetools.channels import CouchbaseChannel
from mousetools.channels.enums import CouchbaseChannels, DestinationTimezones
from mousetools.enums import DestinationShort
from mousetools.mixins.couchbase import CouchbaseMixin

logger = logging.getLogger(__name__)


class ForecastedWaitTimesChildChannel(CouchbaseMixin):
    def __init__(
        self,
        channel_id: str,
        lazy_load: bool = True,
    ):
        """
        Args:
            channel_id (str): Forecasted Wait Times Channel ID
            lazy_load (bool, optional): If True, will not pull data until a method or property is called. Defaults to True.
        """
        if isinstance(channel_id, Enum):
            channel_id = channel_id.value

        self.channel_id: str = channel_id
        self.entity_id: str = channel_id.rsplit(".", 1)[-1]

        self._destination_short: DestinationShort = self.channel_id.split(".")[0]
        self._tz: DestinationTimezones = (
            DestinationTimezones.WALT_DISNEY_WORLD
            if self._destination_short == DestinationShort.WALT_DISNEY_WORLD
            else DestinationTimezones.DISNEYLAND_RESORT
        )
        self._refresh_interval: timedelta = timedelta(minutes=30)

        self._cb_data: typing.Optional[dict] = None
        self._cb_data_pull_time: datetime = datetime.now(tz=self._tz.value)
        if not lazy_load:
            self.refresh()

    def __repr__(self):
        return f"{self.__class__.__name__}(channel_id='{self.channel_id}')"

    def refresh(self) -> None:
        """Pulls initial data if none exists or if it is older than the refresh interval"""
        if self._cb_data is None or datetime.now(tz=self._tz.value) - self.last_update > self._refresh_interval:
            self._cb_data = self.get_channel_data(self.channel_id)
            self._cb_data_pull_time = datetime.now(tz=self._tz.value)

    @property
    def last_update(self) -> datetime:
        """The last time the data was updated.

        Returns:
            (datetime): The last time the entity's data was updated, or None if no such data exists.
        """
        if self._cb_data is None:
            self._cb_data = self.get_channel_data(self.channel_id)

        try:
            dt = isoparse(self._cb_data["lastUpdate"])
            dt = dt.replace(tzinfo=self._tz.value)
            return dt
        except (KeyError, TypeError, ValueError):
            logger.debug("No last updated found for %s", self.channel_id)
            return self._cb_data_pull_time

    def get_forecast(self) -> list[dict]:
        """Returns a list of forecasted wait times sorted by timestamp

        Returns:
            (list[dict]): A list of dictionaries. Each dictionary contains forecasted wait minutes, bar graph percentage, accessibility label, and timestamp
        """
        self.refresh()
        try:
            if "forecasts" not in self._cb_data:
                return []

            forecasts = []
            for forecast in self._cb_data["forecasts"]:
                tmp = {}
                dt = isoparse(forecast["timestamp"])
                dt = dt.astimezone(self._tz.value)
                tmp["forecasted_wait_minutes"] = forecast["forecastedWaitMinutes"]
                tmp["bar_graph_percentage"] = forecast["percentage"]
                tmp["accessibility_label"] = forecast["accessibility12h"].split(" ", 1)[-1]
                tmp["timestamp"] = dt
                forecasts.append(tmp)

            return sorted(forecasts, key=lambda i: i["timestamp"])

        except (KeyError, TypeError, ValueError):
            logger.debug("No forecast found for %s", self.channel_id)
            return []


class ForecastedWaitTimesChannel(CouchbaseChannel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_children_channels(self) -> list[ForecastedWaitTimesChildChannel]:
        """Gets a list of children channels for the channel.

        Returns:
            (list[ForecastedWaitTimesChildChannel]): A list of ForecastedWaitTimesChildChannel
        """
        self.refresh()
        channels = []
        for i in self._cb_data["results"]:
            if CouchbaseChannels.FORECASTED_WAIT_TIMES in i["id"]:
                channels.append(ForecastedWaitTimesChildChannel(i["id"]))
        return channels
