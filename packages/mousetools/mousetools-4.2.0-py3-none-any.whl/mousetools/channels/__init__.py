import typing
from datetime import datetime, timedelta
from enum import Enum

from mousetools.channels.enums import DestinationTimezones, DLRCouchbaseChannels, WDWCouchbaseChannels
from mousetools.enums import DestinationShort, EntityType
from mousetools.mixins.couchbase import CouchbaseMixin


class CouchbaseChannel(CouchbaseMixin):
    def __init__(self, channel_id: typing.Union[WDWCouchbaseChannels, DLRCouchbaseChannels], lazy_load: bool = True):
        """
        Args:
            channel_id (typing.Union[WDWCouchbaseChannels, DLRCouchbaseChannels]): Channel ID from the enum
            lazy_load (bool, optional): If True, will not pull data until a method or property is called. Defaults to True.
        """
        if isinstance(channel_id, Enum):
            channel_id = channel_id.value
        self.channel_id = channel_id

        self._destination_short: DestinationShort = channel_id.split(".")[0]
        self._tz: DestinationTimezones = (
            DestinationTimezones.WALT_DISNEY_WORLD
            if self._destination_short == DestinationShort.WALT_DISNEY_WORLD
            else DestinationTimezones.DISNEYLAND_RESORT
        )

        self._cb_data = None
        self._refresh_interval = timedelta(minutes=10)
        self.last_update = datetime.now(tz=self._tz.value)

        if not lazy_load:
            self.refresh()

    def refresh(self) -> None:
        """Pulls initial data if none exists or if it is older than the refresh interval"""
        if self._cb_data is None or datetime.now(tz=self._tz.value) - self.last_update > self._refresh_interval:
            self._cb_data = self.get_channel_changes(self.channel_id)
            self.last_update = datetime.now(tz=self._tz.value)

    def get_children_channel_ids(self) -> list[str]:
        """Returns a list of child channel ids for the channel."""
        self.refresh()

        return [i["id"] for i in self._cb_data["results"]]

    def _get_children_objects_helper(self, class_obj, entity_type: EntityType) -> list:
        self.refresh()
        channels = []
        check_for = f"entitytype={entity_type.value}".lower()
        for i in self._cb_data["results"]:
            if check_for == i["id"].rsplit(";")[-1].lower():
                channels.append(class_obj(i["id"]))
        return channels

    def __repr__(self):
        return f"{self.__class__.__name__}(channel_id='{self.channel_id}')"

    def __eq__(self, other) -> bool:
        if isinstance(other, CouchbaseChannel):
            return self.channel_id == other.channel_id
        return False
