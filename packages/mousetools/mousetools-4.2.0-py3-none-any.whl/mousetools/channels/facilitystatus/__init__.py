import logging
import typing
from datetime import datetime, timedelta

from dateutil.parser import isoparse

from mousetools.channels import CouchbaseChannel
from mousetools.channels.enums import CouchbaseChannels, DestinationTimezones
from mousetools.decorators import disney_property
from mousetools.enums import DestinationShort, EntityType
from mousetools.mixins.couchbase import CouchbaseMixin

logger = logging.getLogger(__name__)


class FacilityStatusChildChannel(CouchbaseMixin):
    def __init__(self, channel_id: str, lazy_load: bool = True):
        """
        Args:
            channel_id (typing.Union[WDWCouchbaseChannels, DLRCouchbaseChannels]): Channel ID from the enum
            lazy_load (bool, optional): If True, will not pull data until a method or property is called. Defaults to True.
        """
        self.channel_id = channel_id

        self._destination_short: DestinationShort = channel_id.split(".")[0]
        self._tz: DestinationTimezones = (
            DestinationTimezones.WALT_DISNEY_WORLD
            if self._destination_short == DestinationShort.WALT_DISNEY_WORLD
            else DestinationTimezones.DISNEYLAND_RESORT
        )
        self._refresh_interval: timedelta = timedelta(minutes=10)
        self._cb_data: typing.Optional[dict] = None
        self._cb_data_pull_time: datetime = datetime.now(tz=self._tz.value)

        if not lazy_load:
            self.refresh()

    def refresh(self) -> None:
        """Pulls initial data if none exists or if it is older than the refresh interval"""
        if self._cb_data is None or datetime.now(tz=self._tz.value) - self.last_update > self._refresh_interval:
            self._cb_data = self.get_channel_data(self.channel_id)
            self._cb_data_pull_time = datetime.now(tz=self._tz.value)

    def get_status(self) -> typing.Optional[str]:
        """Get the operating status of the facility

        Returns:
            (typing.Optional[str]): Operating status. Typically "Operating" or "Closed".
        """
        self.refresh()

        try:
            return self._cb_data["status"]
        except (KeyError, TypeError, ValueError):
            logger.debug("No status found for %s", self.channel_id)
            return None

    def get_wait_time(self) -> typing.Optional[int]:
        """Get the wait time in minutes

        Returns:
            (typing.Optional[int]): Wait time in minutes
        """
        self.refresh()

        try:
            return self._cb_data["waitMinutes"]
        except (KeyError, TypeError, ValueError):
            logger.debug("No wait time found for %s", self.channel_id)
            return None

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

    @disney_property()
    def fast_pass_available(self) -> typing.Optional[bool]:
        return self._cb_data["fastPassAvailable"]

    def get_fast_pass_end_time(self) -> typing.Optional[datetime]:
        self.refresh()

        try:
            dt = isoparse(self._cb_data["fastPassEndTime"])
            dt = dt.replace(tzinfo=self._tz.value)
            return dt
        except (KeyError, TypeError, ValueError):
            logger.debug("No fast pass end time found for %s", self.channel_id)
            return None

    def get_fast_pass_start_time(self) -> typing.Optional[datetime]:
        self.refresh()

        try:
            dt = isoparse(self._cb_data["fastPassStartTime"])
            dt = dt.replace(tzinfo=self._tz.value)
            return dt
        except (KeyError, TypeError, ValueError):
            logger.debug("No fast pass start time found for %s", self.channel_id)
            return None

    @disney_property()
    def single_rider(self) -> typing.Optional[bool]:
        """Whether the facility allows single riders

        Returns:
            (typing.Optional[bool]): Whether the facility allows single riders
        """
        return self._cb_data["singleRider"]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(channel_id='{self.channel_id}')"

    def __eq__(self, other) -> bool:
        if isinstance(other, FacilityStatusChildChannel):
            return self.channel_id == other.channel_id
        return False


AttractionFacilityStatusChild = type("AttractionFacilityStatusChild", (FacilityStatusChildChannel,), {})
EntertainmentFacilityStatusChild = type("EntertainmentFacilityStatusChild", (FacilityStatusChildChannel,), {})
EntertainmentVenueFacilityStatusChild = type("EntertainmentVenueFacilityStatusChild", (FacilityStatusChildChannel,), {})
LandFacilityStatusChild = type("LandFacilityStatusChild", (FacilityStatusChildChannel,), {})
RestaurantFacilityStatusChild = type("RestaurantFacilityStatusChild", (FacilityStatusChildChannel,), {})
ThemeParkFacilityStatusChild = type("ThemeParkFacilityStatusChild", (FacilityStatusChildChannel,), {})
WaterParkFacilityStatusChild = type("WaterParkFacilityStatusChild", (FacilityStatusChildChannel,), {})


class FacilityStatusChannel(CouchbaseChannel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_children_channels(self) -> list[FacilityStatusChildChannel]:
        """Gets a list of children channels for the channel.

        Returns:
            typing.list[FacilityStatusChildChannel]: A list of FacilityStatusChildChannels
        """
        self.refresh()
        channels = []
        for i in self._cb_data["results"]:
            if CouchbaseChannels.FACILITY_STATUS in i["id"]:
                channels.append(FacilityStatusChildChannel(i["id"]))
        return channels

    def get_children_attractions(self) -> list[AttractionFacilityStatusChild]:  # type: ignore
        """Get AttractionFacilityStatusChild Children of a Facility

        Returns:
            list[AttractionFacilityStatusChild]: A list of AttractionFacilityStatusChild Children
        """
        return self._get_children_objects_helper(AttractionFacilityStatusChild, EntityType.ATTRACTION)

    def get_children_entertainment(self) -> list[EntertainmentFacilityStatusChild]:  # type: ignore
        """Get EntertainmentFacilityStatusChild Children of a Facility

        Returns:
            list[EntertainmentFacilityStatusChild]: A list of EntertainmentFacilityStatusChild Children
        """
        return self._get_children_objects_helper(EntertainmentFacilityStatusChild, EntityType.ENTERTAINMENT)

    def get_children_entertainment_venues(self) -> list[EntertainmentVenueFacilityStatusChild]:  # type: ignore
        """Get EntertainmentVenueFacilityStatusChild Children of a Facility

        Returns:
            list[EntertainmentVenueFacilityStatusChild]: A list of EntertainmentVenueFacilityStatusChild Children
        """
        return self._get_children_objects_helper(EntertainmentVenueFacilityStatusChild, EntityType.ENTERTAINMENT_VENUE)

    def get_children_lands(self) -> list[LandFacilityStatusChild]:  # type: ignore
        """Get LandFacilityStatusChild Children of a Facility

        Returns:
            list[LandFacilityStatusChild]: A list of LandFacilityStatusChild Children
        """
        return self._get_children_objects_helper(LandFacilityStatusChild, EntityType.LAND)

    def get_children_restaurants(self) -> list[RestaurantFacilityStatusChild]:  # type: ignore
        """Get RestaurantFacilityStatusChild Children of a Facility

        Returns:
            list[RestaurantFacilityStatusChild]: A list of RestaurantFacilityStatusChild Children
        """
        return self._get_children_objects_helper(RestaurantFacilityStatusChild, EntityType.RESTAURANT)

    def get_children_theme_parks(self) -> list[ThemeParkFacilityStatusChild]:  # type: ignore
        """Get ThemeParkFacilityStatusChild Children of a Facility

        Returns:
            list[ThemeParkFacilityStatusChild]: A list of ThemeParkFacilityStatusChild Children
        """
        return self._get_children_objects_helper(ThemeParkFacilityStatusChild, EntityType.THEME_PARK)

    def get_children_water_parks(self) -> list[WaterParkFacilityStatusChild]:  # type: ignore
        """Get WaterParkFacilityStatusChild Children of a Facility

        Returns:
            list[WaterParkFacilityStatusChild]: A list of WaterParkFacilityStatusChild Children
        """
        return self._get_children_objects_helper(WaterParkFacilityStatusChild, EntityType.WATER_PARK)
