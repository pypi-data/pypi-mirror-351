import logging
import os
import typing
from datetime import datetime, time, timedelta
from enum import Enum
from zoneinfo import ZoneInfo

import httpx
from dateutil.parser import isoparse

from mousetools.api.menu import Menus
from mousetools.channels import CouchbaseChannel
from mousetools.channels.calendar import CalendarChildChannel
from mousetools.channels.enums import (
    CouchbaseChannels,
    DestinationTimezones,
    DLRCouchbaseChannels,
    WDWCouchbaseChannels,
)
from mousetools.channels.facilitystatus import FacilityStatusChildChannel
from mousetools.channels.forecastedwaittimes import ForecastedWaitTimesChildChannel
from mousetools.decorators import disney_property
from mousetools.enums import DestinationShort, EntityType
from mousetools.mixins.couchbase import CouchbaseMixin

logger = logging.getLogger(__name__)


class FacilityChildChannel(CouchbaseMixin):
    """Base class for all Facility Child Channels. Subclasses like Attraction, Restaurant, Entertainment, etc. extend this class.

    Example:

        >>> from mousetools.channels.facilities import AttractionFacilityChild, ThemeParkFacilityChild
        >>> a = AttractionFacilityChild("wdw.facilities.1_0.en_us.attraction.80010177;entityType=Attraction")
        >>> print(a)
        "Attraction: Pirates of the Caribbean (wdw.facilities.1_0.en_us.attraction.80010177;entityType=Attraction)"
        >>> from mousetools.channels.facilities.enums import WaltDisneyWorldParkChannelIds
        >>> d = ThemeParkFacilityChild(WaltDisneyWorldParkChannelIds.MAGIC_KINGDOM, lazy_load=False)
        >>> print(d.coordinates)
        {'latitude': 28.4160036778, 'longitude': -81.5811902834}
    """

    def __init__(
        self,
        channel_id: str,
        lazy_load: bool = True,
    ):
        """
        Args:
            channel_id (str): Facility Channel ID
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
        self._refresh_interval: timedelta = timedelta(
            hours=12
        )  # properties are rarely updated, no need to spam the API

        self._cb_data: typing.Optional[dict] = None
        self._cb_data_pull_time: datetime = datetime.now(tz=self._tz.value)
        if not lazy_load:
            self.refresh()

        self._today_calendar: typing.Optional[CalendarChildChannel] = None

    def refresh(self) -> None:
        """Pulls initial data if none exists or if it is older than the refresh interval"""
        if self._cb_data is None or datetime.now(tz=self._tz.value) - self.last_update > self._refresh_interval:
            self._cb_data = self.get_channel_data(self.channel_id)
            self._cb_data_pull_time = datetime.now(tz=self._tz.value)

    def pull_today_calendar(self) -> None:
        """Pulls today's calendar.

        Calling this method will automatically refresh the calendar to today even if a calendar exists.
        """
        today = datetime.now(tz=self._tz.value)
        day = today.day
        month = today.month

        calendar_channel_id = f"{WDWCouchbaseChannels.CALENDAR.value if self._destination_short == DestinationShort.WALT_DISNEY_WORLD else DLRCouchbaseChannels.CALENDAR.value}.{day:02}-{month:02}."
        self._today_calendar = CalendarChildChannel(calendar_channel_id)

    @disney_property()
    def name(self) -> typing.Optional[str]:
        """
        The name of the entity.

        Returns:
            (typing.Optional[str]): The name of the entity, or None if it was not found.
        """

        return self._cb_data["name"]

    @disney_property()
    def entity_type(self) -> typing.Optional[str]:
        """
        The type of entity this is.

        Returns:
            (typing.Optional[str]): The type of entity this is, or None if it was not found.
        """
        return self._cb_data["type"]

    @disney_property()
    def sub_type(self) -> typing.Optional[str]:
        """
        The sub type of entity.

        Returns:
            (typing.Optional[str]): The sub type of entity, or None if it was not found.
        """
        return self._cb_data["subType"]

    @disney_property()
    def coordinates(self) -> typing.Optional[dict[str, float]]:
        """
        The coordinates of this entity

        Returns:
            (typing.Optional[dict[str, float]]): A dict with "lat" and "lng" keys containing the coordinates of this entity as floats, or None if no coordinates are found
        """
        return {
            "latitude": float(self._cb_data["latitude"]),
            "longitude": float(self._cb_data["longitude"]),
        }

    @disney_property()
    def ancestor_destination_entity_id(self) -> typing.Optional[str]:  # type: ignore
        """
        The id of the ancestor destination of this entity.

        Returns:
            (typing.Optional[str]): The id of the ancestor destination of this entity, or None if it was not found.
        """
        return self._cb_data["ancestorDestinationId"]

    @disney_property()
    def ancestor_theme_park_entity_id(self):
        """
        The id of the theme park of this entity.

        Returns:
            (typing.Optional[str]): Theme park id, or None if no such id is found.
        """
        return self._cb_data["ancestorThemeParkId"]

    @disney_property()
    def ancestor_water_park_entity_id(self) -> typing.Optional[str]:
        """
        The if of the water park of this entity.

        Returns:
            (typing.Optional[str]): Water park id, or None if no such id is found.
        """
        return self._cb_data["ancestorWaterParkId"]

    @disney_property()
    def ancestor_resort_entity_id(self) -> typing.Optional[str]:
        """
        The id of the resort of the entity.

        Returns:
            (typing.Optional[str): Resort id, or None if no such id is found.
        """
        return self._cb_data["ancestorResortId"]

    @disney_property()
    def ancestor_land_entity_id(self) -> typing.Optional[str]:
        """
        The if of the land of this entity.

        Returns:
            (typing.Optional[str]): Land id, or None if no such id is found.
        """
        return self._cb_data["ancestorLandId"]

    @disney_property()
    def ancestor_resort_area_entity_id(self) -> typing.Optional[str]:
        """
        The id of the resort area of this entity.

        Returns:
            (typing.Optional[str]): Resort area id, or None if no such id is found.
        """
        return self._cb_data["ancestorResortAreaId"]

    @disney_property()
    def ancestor_entertainment_venue_entity_id(self) -> typing.Optional[str]:
        """
        The id of entertainment venues of this entity.

        Returns:
            (typing.Optional[str]): Entertainment venue id, or None if no such id is found.
        """
        return self._cb_data["ancestorEntertainmentVenueId"]

    @disney_property()
    def ancestor_restaurant_entity_id(self) -> typing.Optional[str]:
        """
        The id of the restaurant of this entity.

        Returns:
            (typing.Optional[str]): Restaurant id, or None if no such id is found.
        """
        return self._cb_data["ancestorRestaurantId"]

    @disney_property()
    def ancestor_destination_name(self) -> typing.Optional[str]:
        """
        The name of the destination of this entity.

        Returns:
            (typing.Optional[str]): Destination name, or None if no such name is found.
        """
        return self._cb_data["ancestorDestination"]

    @disney_property()
    def ancestor_resort_name(self) -> typing.Optional[str]:
        """
        The name of the resort of this entity.

        Returns:
            (typing.Optional[str]): Resort name, or None if no such name is found.
        """
        return self._cb_data["ancestorResort"]

    @disney_property()
    def ancestor_land_name(self) -> typing.Optional[str]:
        """
        The name of the land of this entity.

        Returns:
            (typing.Optional[str]): Land name, or None if no such name is found.
        """
        return self._cb_data["ancestorLand"]

    @disney_property()
    def ancestor_resort_area_name(self) -> typing.Optional[str]:
        """
        The name of the resort area of this entity.

        Returns:
            (typing.Optional[str]): Resort area name, or None if no such name is found.
        """
        return self._cb_data["ancestorResortArea"]

    @disney_property()
    def ancestor_entertainment_venue_name(self) -> typing.Optional[str]:
        """
        The name of the entertainment venue of this entity.

        Returns:
            (typing.Optional[str]): Entertainment venue name, or None if no such name is found.
        """
        return self._cb_data["ancestorEntertainmentVenue"]

    @disney_property()
    def ancestor_restaurant_name(self) -> typing.Optional[str]:
        """
        The name of the restaurant of this entity.

        Returns:
            (typing.Optional[str]): Restaurant name, or None if no such name is found.
        """
        return self._cb_data["ancestorRestaurant"]

    @disney_property()
    def ancestor_theme_park_name(self) -> typing.Optional[str]:
        """
        The name of the theme park of this entity.

        Returns:
            (typing.Optional[str]): Theme park name, or None if no such name is found.
        """
        return self._cb_data["ancestorThemePark"]

    @disney_property()
    def ancestor_water_park_name(self) -> typing.Optional[str]:
        """
        The name of the water park of this entity.

        Returns:
            (typing.Optional[str]): Water park name, or None if no such name is found.
        """
        return self._cb_data["ancestorWaterPark"]

    @disney_property()
    def disney_owned(self) -> typing.Optional[bool]:
        """
        Whether the entity is owned by Disney.

        Returns:
            (typing.Optional[bool]): Whether the entity is owned by Disney.
        """
        return self._cb_data["disneyOwned"]

    @disney_property()
    def disney_operated(self) -> typing.Optional[bool]:
        """
        Whether the entity is operated by Disney.

        Returns:
            (typing.Optional[bool]): Whether the entity is operated by Disney.
        """
        return self._cb_data["disneyOperated"]

    @disney_property()
    def admission_required(self) -> typing.Optional[bool]:
        """
        Whether the entity requires admission.

        Returns:
            (typing.Optional[bool]): Whether the entity requires admission.
        """
        return self._cb_data["admissionRequired"]

    @disney_property()
    def pre_paid(self) -> typing.Optional[bool]:
        """
        Whether the entity is pre-paid.

        Returns:
            (typing.Optional[bool]): Whether the entity is pre-paid.
        """
        return self._cb_data["prePaid"]

    @property
    def timezone(self) -> ZoneInfo:
        """
        The time zone of the entity.

        Returns:
            (ZoneInfo): The time zone of the entity.
        """

        return self._tz.value

    @disney_property()
    def related_location_ids(self) -> list[str]:
        """
        The ids of the related locations of this entity.

        Returns:
            (list[str]): The ids of the related locations of this entity.
        """
        # https://api.wdprapps.disney.com/facility-service/entertainments/19322758
        raise NotImplementedError

    @disney_property()
    def duration(self) -> typing.Optional[time]:
        """
        The duration of the entity.

        Returns:
            (typing.Optional[time]): The duration of the entity.
        """
        return time.fromisoformat(":".join(self._cb_data["duration"].split(":")[:3]))

    @disney_property()
    def description(self) -> typing.Optional[str]:
        """The description of the facility.

        Returns:
            (typing.Optional[str]): The description of the entity.
        """
        return self._cb_data["description"]

    def get_facility_status_channel(self) -> FacilityStatusChildChannel:
        """Get the facility status channel for this entity.

        Returns:
            (FacilityStatusChildChannel): The facility status channel
        """
        channel = (
            WDWCouchbaseChannels.FACILITY_STATUS
            if self._destination_short == DestinationShort.WALT_DISNEY_WORLD
            else DLRCouchbaseChannels.FACILITY_STATUS
        )
        facility_status_channel_id = f"{channel.value}.{self.entity_id}"

        return FacilityStatusChildChannel(facility_status_channel_id)

    @property
    def last_update(self) -> datetime:
        """
        The last time the data was updated.

        Returns:
            (datetime): The last time the entity's data was updated, or None if no such data exists.
        """
        if self._cb_data is None:
            self._cb_data = self.get_channel_data(self.channel_id)

        try:
            tz = (
                DestinationTimezones.WALT_DISNEY_WORLD
                if "wdw" in self.channel_id
                else DestinationTimezones.DISNEYLAND_RESORT
            )
            dt = isoparse(self._cb_data["lastUpdate"])
            dt = dt.replace(tzinfo=tz.value)
            return dt
        except (KeyError, TypeError, ValueError):
            logger.debug("No last updated found for %s", self.channel_id)
            return self._cb_data_pull_time

    @disney_property()
    def sponsor_name(self) -> typing.Optional[str]:
        """The sponsor name of the entity.

        Returns:
            (typing.Optional[str]): The sponsor name of the entity.
        """
        return self._cb_data["sponsorName"]

    @disney_property()
    def meal_periods(self) -> typing.Optional[list[str]]:
        """
        The meal periods offered by the restaurant.

        Returns:
            (typing.Optional[list[str]]): The meal periods offered by the restaurant.
        """
        return self._cb_data["mealPeriods"]

    def get_menu(self) -> Menus:
        """
        The menu of the restaurant.

        Returns:
            (Menus): The menu of the restaurant.
        """
        return Menus(self.channel_id)

    def get_forecasted_wait_times_channel(self) -> ForecastedWaitTimesChildChannel:
        """Get the forecasted wait times channel for this entity.

        Returns:
            (ForecastedWaitTimesChildChannel): The forecasted wait times channel

        Example:
            ```python
            >>> f = FacilityChildChannel("wdw.facilities.1_0.en_us.attraction.80010177;entityType=Attraction", lazy_load=False)
            >>> fwt = f.get_forecasted_wait_times_channel()
            >>> fwt.get_forecast()
            [{'forecasted_wait_minutes': 85, 'bar_graph_percentage': 70, 'accessibility_label': 'High', 'timestamp': datetime.datetime(2025, 5, 27, 9, 0, tzinfo=zoneinfo.ZoneInfo(key='America/New_York'))}, ...]
            ```
        """
        channel_id = f"{WDWCouchbaseChannels.FORECASTED_WAIT_TIMES.value if self._destination_short == DestinationShort.WALT_DISNEY_WORLD else DLRCouchbaseChannels.FORECASTED_WAIT_TIMES.value}.{self.entity_id}"
        return ForecastedWaitTimesChildChannel(channel_id)

    @disney_property()
    def detail_image_url(self) -> typing.Optional[str]:
        """The detail image url of the entity.

        Returns:
            (typing.Optional[str]): The detail image url of the entity.
        """
        return self._cb_data["detailImageUrl"]

    @disney_property()
    def list_image_url(self) -> typing.Optional[str]:
        """The list image url of the entity.

        Returns:
            (typing.Optional[str]): The list image url of the entity.
        """
        return self._cb_data["listImageUrl"]

    def get_today_park_hours(self) -> dict:
        """Get the park hours for today.

        Returns:
            (dict): The park hours for today.
        """
        self.pull_today_calendar()
        hours = self._today_calendar.get_park_hours(self.entity_id)
        return hours

    def get_today_meal_periods(self) -> dict:
        """Get the meal periods for today.

        Returns:
            (dict): The meal periods for today.
        """
        self.pull_today_calendar()
        meal_periods = self._today_calendar.get_meal_periods(self.entity_id)
        return meal_periods

    def get_today_schedule(self) -> list[dict]:
        """Get the schedule for today.

        Returns:
            (list[dict]): The schedule for today.
        """
        self.pull_today_calendar()
        schedule = self._today_calendar.get_facility_schedule(self.entity_id)
        return schedule

    def is_closed_today(self) -> bool:
        """Check if the facility is closed today.

        Returns:
            (bool): True if the facility is closed today, False otherwise.
        """
        self.pull_today_calendar()
        refurb = self._today_calendar.get_refurbishment(self.entity_id)
        closed = self._today_calendar.get_closed(self.entity_id)
        return bool(refurb or closed)

    def get_current_weather(self, api_key: typing.Optional[str] = None) -> dict:
        """Get the current weather for the facility using the OpenWeatherMap API. https://openweathermap.org

        Args:
            api_key (typing.Optional[str], optional): The API key to use. Defaults to None. If None, will use the MT_OPEN_WEATHER_API_KEY environment variable.

        Returns:
            (dict): The current weather for the facility.
        """

        weather_key = api_key or os.environ.get("MT_OPEN_WEATHER_API_KEY")

        if weather_key is None:
            logger.warning("No weather API key found")
            return {}

        coordinates = self.coordinates
        if coordinates is None:
            return {}

        weather_url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": coordinates["latitude"],
            "lon": coordinates["longitude"],
            "appid": weather_key,
        }
        try:
            response = httpx.get(weather_url, params=params)
            response.raise_for_status()
            data = response.json()
            return data
        except httpx.HTTPError as err:
            logger.error("Request failed: %s", err)
            return {}

    def __str__(self) -> str:
        return f"{self.entity_type}: {self.name} ({self.channel_id})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(channel_id='{self.channel_id}')"

    def __eq__(self, other) -> bool:
        if isinstance(other, FacilityChildChannel):
            return self.channel_id == other.channel_id
        return False


AttractionFacilityChild = type("AttractionFacilityChild", (FacilityChildChannel,), {})
AudioTourFacilityChild = type("AudioTourFacilityChild", (FacilityChildChannel,), {})
BuildingFacilityChild = type("BuildingFacilityChild", (FacilityChildChannel,), {})
BusStopFacilityChild = type("BusStopFacilityChild", (FacilityChildChannel,), {})
DestinationFacilityChild = type("DestinationFacilityChild", (FacilityChildChannel,), {})
DiningEventFacilityChild = type("DiningEventFacilityChild", (FacilityChildChannel,), {})
DinnerShowFacilityChild = type("DinnerShowFacilityChild", (FacilityChildChannel,), {})
EntertainmentFacilityChild = type("EntertainmentFacilityChild", (FacilityChildChannel,), {})
EntertainmentVenueFacilityChild = type("EntertainmentVenueFacilityChild", (FacilityChildChannel,), {})
WaterParkFacilityChild = type("WaterParkFacilityChild", (FacilityChildChannel,), {})
GuestServiceFacilityChild = type("GuestServiceFacilityChild", (FacilityChildChannel,), {})
LandFacilityChild = type("LandFacilityChild", (FacilityChildChannel,), {})
MerchandiseFacilityChild = type("MerchandiseFacilityChild", (FacilityChildChannel,), {})
PhotopassFacilityChild = type("PhotopassFacilityChild", (FacilityChildChannel,), {})
PointOfInterestFacilityChild = type("PointOfInterestFacilityChild", (FacilityChildChannel,), {})
RecreationFacilityChild = type("RecreationFacilityChild", (FacilityChildChannel,), {})
RecreationActivityFacilityChild = type("RecreationActivityFacilityChild", (FacilityChildChannel,), {})
ResortFacilityChild = type("ResortFacilityChild", (FacilityChildChannel,), {})
ResortAreaFacilityChild = type("ResortAreaFacilityChild", (FacilityChildChannel,), {})
SpaFacilityChild = type("SpaFacilityChild", (FacilityChildChannel,), {})
ThemeParkFacilityChild = type("ThemeParkFacilityChild", (FacilityChildChannel,), {})
TourFacilityChild = type("TourFacilityChild", (FacilityChildChannel,), {})
TransportationFacilityChild = type("TransportationFacilityChild", (FacilityChildChannel,), {})
WaterParkFacilityChild = type("WaterParkFacilityChild", (FacilityChildChannel,), {})
RestaurantFacilityChild = type("RestaurantFacilityChild", (FacilityChildChannel,), {})


class FacilityChannel(CouchbaseChannel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_children_channels(self) -> list[FacilityChildChannel]:
        """Gets a list of children channels for the channel.

        Returns:
            (list[FacilityChildChannel]): A list of FacilityChildChannel
        """
        self.refresh()
        channels = []
        for i in self._cb_data["results"]:
            if CouchbaseChannels.FACILITIES in i["id"]:
                channels.append(FacilityChildChannel(i["id"]))
        return channels

    def get_children_attractions(self) -> list[AttractionFacilityChild]:  # type: ignore
        """Get AttractionFacilityChild Children of a Facility

        Returns:
            (list[AttractionFacilityChild]): A list of AttractionFacilityChild Children
        """
        return self._get_children_objects_helper(AttractionFacilityChild, EntityType.ATTRACTION)

    def get_children_audio_tours(self) -> list[AudioTourFacilityChild]:  # type: ignore
        """Get AudioTourFacilityChild Children of a Facility

        Returns:
            (list[AudioTourFacilityChild]): A list of AudioTourFacilityChild Children
        """
        return self._get_children_objects_helper(AudioTourFacilityChild, EntityType.AUDIO_TOUR)

    def get_children_buildings(self) -> list[BuildingFacilityChild]:  # type: ignore
        """Get BuildingFacilityChild Children of a Facility

        Returns:
            (list[BuildingFacilityChild]): A list of BuildingFacilityChild Children
        """
        return self._get_children_objects_helper(BuildingFacilityChild, EntityType.BUILDING)

    def get_children_bus_stops(self) -> list[BusStopFacilityChild]:  # type: ignore
        """Get BusStopFacilityChild Children of a Facility

        Returns:
            (list[BusStopFacilityChild]): A list of BusStopFacilityChild Children
        """
        return self._get_children_objects_helper(BusStopFacilityChild, EntityType.BUS_STOP)

    def get_children_destinations(self) -> list[DestinationFacilityChild]:  # type: ignore
        """Get DestinationFacilityChild Children of a Facility

        Returns:
            (list[DestinationFacilityChild]): A list of DestinationFacilityChild Children
        """
        return self._get_children_objects_helper(DestinationFacilityChild, EntityType.DESTINATION)

    def get_children_dining_events(self) -> list[DiningEventFacilityChild]:  # type: ignore
        """Get DiningEventFacilityChild Children of a Facility

        Returns:
            (list[DiningEventFacilityChild]): A list of DiningEventFacilityChild Children
        """
        return self._get_children_objects_helper(DiningEventFacilityChild, EntityType.DINING_EVENT)

    def get_children_dinner_shows(self) -> list[DinnerShowFacilityChild]:  # type: ignore
        """Get DinnerShowFacilityChild Children of a Facility

        Returns:
            (list[DinnerShowFacilityChild]): A list of DinnerShowFacilityChild Children
        """
        return self._get_children_objects_helper(DinnerShowFacilityChild, EntityType.DINNER_SHOW)

    def get_children_entertainment(self) -> list[EntertainmentFacilityChild]:  # type: ignore
        """Get EntertainmentFacilityChild Children of a Facility

        Returns:
            (list[EntertainmentFacilityChild]): A list of EntertainmentFacilityChild Children
        """
        return self._get_children_objects_helper(EntertainmentFacilityChild, EntityType.ENTERTAINMENT)

    def get_children_events(self) -> list[WaterParkFacilityChild]:  # type: ignore
        """Get WaterParkFacilityChild Children of a Facility

        Returns:
            (list[WaterParkFacilityChild]): A list of WaterParkFacilityChild Children
        """
        return self._get_children_objects_helper(WaterParkFacilityChild, EntityType.EVENT)

    def get_children_entertainment_venues(self) -> list[EntertainmentVenueFacilityChild]:  # type: ignore
        """Get EntertainmentVenueFacilityChild Children of a Facility

        Returns:
            (list[EntertainmentVenueFacilityChild]): A list of EntertainmentVenueFacilityChild Children
        """
        return self._get_children_objects_helper(EntertainmentVenueFacilityChild, EntityType.ENTERTAINMENT_VENUE)

    def get_children_guest_services(self) -> list[GuestServiceFacilityChild]:  # type: ignore
        """Get GuestServiceFacilityChild Children of a Facility

        Returns:
            (list[GuestServiceFacilityChild]): A list of GuestServiceFacilityChild Children
        """
        return self._get_children_objects_helper(GuestServiceFacilityChild, EntityType.GUEST_SERVICE)

    def get_children_lands(self) -> list[LandFacilityChild]:  # type: ignore
        """Get LandFacilityChild Children of a Facility

        Returns:
            (list[LandFacilityChild]): A list of LandFacilityChild Children
        """
        return self._get_children_objects_helper(LandFacilityChild, EntityType.LAND)

    def get_children_merchandise_facilities(self) -> list[MerchandiseFacilityChild]:  # type: ignore
        """Get MerchandiseFacilityChild Children of a Facility

        Returns:
            (list[MerchandiseFacilityChild]): A list of MerchandiseFacilityChild Children
        """
        return self._get_children_objects_helper(MerchandiseFacilityChild, EntityType.MERCHANDISE_FACILITY)

    def get_children_photopasses(self) -> list[PhotopassFacilityChild]:  # type: ignore
        """Get PhotopassFacilityChild Children of a Facility

        Returns:
            (list[PhotopassFacilityChild]): A list of PhotopassFacilityChild Children
        """
        return self._get_children_objects_helper(PhotopassFacilityChild, EntityType.PHOTOPASS)

    def get_children_point_of_interests(self) -> list[PointOfInterestFacilityChild]:  # type: ignore
        """Get PointOfInterestFacilityChild Children of a Facility

        Returns:
            (list[PointOfInterestFacilityChild]): A list of PointOfInterestFacilityChild Children
        """
        return self._get_children_objects_helper(PointOfInterestFacilityChild, EntityType.POINT_OF_INTEREST)

    def get_children_recreation(self) -> list[RecreationFacilityChild]:  # type: ignore
        """Get RecreationFacilityChild Children of a Facility

        Returns:
            (list[RecreationFacilityChild]): A list of RecreationFacilityChild Children
        """
        return self._get_children_objects_helper(RecreationFacilityChild, EntityType.RECREATION)

    def get_children_recreation_activities(self) -> list[RecreationActivityFacilityChild]:  # type: ignore
        """Get RecreationActivityFacilityChild Children of a Facility

        Returns:
            (list[RecreationActivityFacilityChild]): A list of RecreationActivityFacilityChild Children
        """
        return self._get_children_objects_helper(RecreationActivityFacilityChild, EntityType.RECREATION_ACTIVITY)

    def get_children_resorts(self) -> list[ResortFacilityChild]:  # type: ignore
        """Get ResortFacilityChild Children of a Facility

        Returns:
            (list[ResortFacilityChild]): A list of ResortFacilityChild Children
        """
        return self._get_children_objects_helper(ResortFacilityChild, EntityType.RESORT)

    def get_children_resort_areas(self) -> list[ResortAreaFacilityChild]:  # type: ignore
        """Get ResortAreaFacilityChild Children of a Facility

        Returns:
            (list[ResortAreaFacilityChild]): A list of ResortAreaFacilityChild Children
        """
        return self._get_children_objects_helper(ResortAreaFacilityChild, EntityType.RESORT_AREA)

    def get_children_restaurants(self) -> list[RestaurantFacilityChild]:  # type: ignore
        """Get RestaurantFacilityChild Children of a Facility

        Returns:
            (list[RestaurantFacilityChild]): A list of RestaurantFacilityChild Children
        """
        return self._get_children_objects_helper(RestaurantFacilityChild, EntityType.RESTAURANT)

    def get_children_spas(self) -> list[SpaFacilityChild]:  # type: ignore
        """Get SpaFacilityChild Children of a Facility

        Returns:
            (list[SpaFacilityChild]): A list of SpaFacilityChild Children
        """
        return self._get_children_objects_helper(SpaFacilityChild, EntityType.SPA)

    def get_children_theme_parks(self) -> list[ThemeParkFacilityChild]:  # type: ignore
        """Get ThemeParkFacilityChild Children of a Facility

        Returns:
            (list[ThemeParkFacilityChild]): A list of ThemeParkFacilityChild Children
        """
        return self._get_children_objects_helper(ThemeParkFacilityChild, EntityType.THEME_PARK)

    def get_children_tours(self) -> list[TourFacilityChild]:  # type: ignore
        """Get TourFacilityChild Children of a Facility

        Returns:
            (list[TourFacilityChild]): A list of TourFacilityChild Children
        """
        return self._get_children_objects_helper(TourFacilityChild, EntityType.TOUR)

    def get_children_transportation(self) -> list[TransportationFacilityChild]:  # type: ignore
        """Get TransportationFacilityChild Children of a Facility

        Returns:
            (list[TransportationFacilityChild]): A list of TransportationFacilityChild Children
        """
        return self._get_children_objects_helper(TransportationFacilityChild, EntityType.TRANSPORTATION)

    def get_children_water_parks(self) -> list[WaterParkFacilityChild]:  # type: ignore
        """Get WaterParkFacilityChild Children of a Facility

        Returns:
            (list[WaterParkFacilityChild]): A list of WaterParkFacilityChild Children
        """
        return self._get_children_objects_helper(WaterParkFacilityChild, EntityType.WATER_PARK)
