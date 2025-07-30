import logging
import typing
from datetime import datetime, timedelta
from enum import Enum
from zoneinfo import ZoneInfo

from dateutil.parser import isoparse

from mousetools.channels import CouchbaseChannel
from mousetools.channels.enums import CouchbaseChannels, DestinationTimezones
from mousetools.decorators import disney_property
from mousetools.enums import DestinationShort
from mousetools.mixins.couchbase import CouchbaseMixin

logger = logging.getLogger(__name__)


class CalendarChildChannel(CouchbaseMixin):
    def __init__(
        self,
        channel_id: str,
        lazy_load: bool = True,
    ):
        """
        Args:
            channel_id (str): Calendar Channel ID
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

    @disney_property()
    def calendar_id(self) -> typing.Optional[str]:
        """The ID of the calendar

        Returns:
            (typing.Optional[str]): The ID of the calendar, or None if no such data exists.
        """
        return self._cb_data["id"]

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
        except (KeyError, ValueError, TypeError):
            logger.debug("No last updated found for %s", self.channel_id)
            return self._cb_data_pull_time

    @disney_property()
    def all_closed(self) -> typing.Optional[list[dict]]:
        """The list of closed facilities.

        Returns:
            (typing.Optional[list[dict]]): The list of closed facilities, or None if no such data exists.
        """
        return self._cb_data["closed"]

    @disney_property()
    def all_facility_schedules(self) -> typing.Optional[dict[str, list[dict]]]:
        """The list of facility schedules.

        Returns:
            (typing.Optional[dict[str, list[dict]]]): The list of facility schedules, or None if no such data exists.
        """
        return self._cb_data["facilitySchedules"]

    @disney_property()
    def all_meal_periods(self) -> typing.Optional[dict[str, list[dict]]]:
        """The list of meal periods.

        Returns:
            (typing.Optional[dict[str, list[dict]]]): The list of meal periods, or None if no such data exists.
        """
        return self._cb_data["mealPeriods"]

    @disney_property()
    def all_park_hours(self) -> typing.Optional[list[dict]]:
        """The list of park hours.

        Returns:
            (typing.Optional[list[dict]]): The list of park hours, or None if no such data exists.
        """
        return self._cb_data["parkHours"]

    @disney_property()
    def all_private_events(self) -> typing.Optional[list[dict]]:
        """The list of private events.

        Returns:
            (typing.Optional[list[dict]]): The list of private events, or None if no such data exists.
        """
        return self._cb_data["privateEvents"]

    @disney_property()
    def all_refurbishments(self) -> typing.Optional[list[dict]]:
        """The list of refurbishments.

        Returns:
            (typing.Optional[list[dict]]): The list of refurbishments, or None if no such data exists.
        """
        return self._cb_data["refurbishments"]

    @property
    def timezone(self) -> ZoneInfo:
        """The timezone of the calendar.

        Returns:
            (ZoneInfo): The timezone of the calendar.
        """
        return self._tz.value

    def get_park_hours(self, entity_id: str) -> dict:
        """Get the park hours for the given entity

        Args:
            entity_id (str): entity id of the facility

        Returns:
            (dict): park hours broken up into their schedule types (Operating, Early Entry, etc.)
        """
        hours = {}
        if self.all_park_hours:
            for i in self.all_park_hours:
                if entity_id in i["facilityId"]:
                    hours[i["scheduleType"]] = {}
                    hours[i["scheduleType"]]["start"] = isoparse(i["startTime"]).astimezone(self._tz.value)
                    hours[i["scheduleType"]]["end"] = isoparse(i["endTime"]).astimezone(self._tz.value)
        return hours

    def get_meal_periods(self, entity_id: str) -> dict:
        """Get the meal periods for the given entity

        Args:
            entity_id (str): entity id of the facility

        Returns:
            (dict): meal periods
        """
        periods = {}
        if self.all_meal_periods:
            restaurant = self.all_meal_periods.get(entity_id, [])
            for i in restaurant:
                meal_period = i["facilityId"]
                periods[meal_period] = {}
                periods[meal_period]["start"] = isoparse(i["startTime"]).astimezone(self._tz.value)
                periods[meal_period]["end"] = isoparse(i["endTime"]).astimezone(self._tz.value)
                periods[meal_period]["schedule_type"] = i["scheduleType"]
        return periods

    def get_refurbishment(self, entity_id: str) -> dict:
        """Get the refurbishment info for the given entity

        Args:
            entity_id (str): entity id of the facility

        Returns:
            (dict): refurbishments
        """
        refurbishments = {}
        if self.all_refurbishments:
            for i in self.all_refurbishments:
                if entity_id in i["facilityId"]:
                    refurbishments["start"] = isoparse(i["startTime"]).astimezone(self._tz.value)
                    refurbishments["end"] = isoparse(i["endTime"]).astimezone(self._tz.value)
        return refurbishments

    def get_closed(self, entity_id: str) -> dict:
        """Get the closed info for the given entity

        Args:
            entity_id (str): entity id of the facility

        Returns:
            (dict): closed
        """
        closed = {}
        if self.all_closed:
            for i in self.all_closed:
                if entity_id in i["facilityId"]:
                    closed["start"] = isoparse(i["startTime"]).astimezone(self._tz.value)
                    closed["end"] = isoparse(i["endTime"]).astimezone(self._tz.value)
        return closed

    def get_facility_schedule(self, entity_id: str) -> list[dict]:
        """Get the schedule info for the given entity

        Args:
            entity_id (str): entity id of the facility

        Returns:
            (list[dict]): schedules
        """
        schedules = []
        if self.all_facility_schedules:
            facility = self.all_facility_schedules.get(entity_id, [])
            for i in facility:
                tmp = {}
                tmp["start"] = isoparse(i["startTime"]).astimezone(self._tz.value)
                tmp["end"] = isoparse(i["endTime"]).astimezone(self._tz.value)
                tmp["schedule_type"] = i["scheduleType"]
                schedules.append(tmp)
        return sorted(schedules, key=lambda i: i["start"])


class CalendarChannel(CouchbaseChannel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.available_calendars = {}
        self.refresh_calendars()

    def refresh_calendars(self):
        """Refreshes the available calendars."""
        available_calendars = {}
        for i in self.get_children_channels():
            available_calendars[i.entity_id] = i

        self.available_calendars = available_calendars

    def get_children_channels(self) -> list[CalendarChildChannel]:
        """Gets a list of children channels for the channel.

        Returns:
            (list[CalendarChildChannel]): A list of CalendarChildChannel
        """
        self.refresh()
        channels = []
        for i in self._cb_data["results"]:
            if CouchbaseChannels.CALENDAR in i["id"]:
                channels.append(CalendarChildChannel(i["id"]))
        return channels

    def get_calendar(self, day: int, month: int) -> typing.Optional[CalendarChildChannel]:
        """Get the calendar for the given day and month

        Args:
            day (int): day of the month
            month (int): month of the year

        Returns:
            (typing.Optional[CalendarChildChannel]): calendar for the given day and month
        """
        self.refresh_calendars()
        return self.available_calendars.get(f"{day:02}-{month:02}", None)
