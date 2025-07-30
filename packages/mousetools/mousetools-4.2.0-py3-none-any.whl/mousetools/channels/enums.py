from enum import Enum
from zoneinfo import ZoneInfo

from mousetools.enums import DestinationShort


class CouchbaseChannels(str, Enum):
    FACILITIES = "facilities"
    FACILITY_STATUS = "facilitystatus"
    CALENDAR = "calendar"
    FORECASTED_WAIT_TIMES = "forecastedwaittimes"
    TODAY = "today"
    CHARACTERS = "characters"


def get_complete_channel_id(
    destination_short: DestinationShort, channel: CouchbaseChannels, version: str, is_multi_language: bool
) -> str:
    channel_id = f"{destination_short.value}.{channel.value}.{version}"

    if is_multi_language:
        channel_id += ".en_us"

    return channel_id


class WDWCouchbaseChannels(str, Enum):
    FACILITIES = get_complete_channel_id(DestinationShort.WALT_DISNEY_WORLD, CouchbaseChannels.FACILITIES, "1_0", True)
    """Walt Disney World Facilities Channel"""
    FACILITY_STATUS = get_complete_channel_id(
        DestinationShort.WALT_DISNEY_WORLD, CouchbaseChannels.FACILITY_STATUS, "1_0", False
    )
    """Walt Disney World Facility Status Channel"""
    CALENDAR = get_complete_channel_id(DestinationShort.WALT_DISNEY_WORLD, CouchbaseChannels.CALENDAR, "1_0", False)
    """Walt Disney World Calendar Channel"""
    FORECASTED_WAIT_TIMES = get_complete_channel_id(
        DestinationShort.WALT_DISNEY_WORLD, CouchbaseChannels.FORECASTED_WAIT_TIMES, "1_0", True
    )
    """Walt Disney World Forecasted Wait Time Channel"""
    TODAY = get_complete_channel_id(DestinationShort.WALT_DISNEY_WORLD, CouchbaseChannels.TODAY, "1_0", False)
    """Walt Disney World Today Channel"""
    CHARACTERS = get_complete_channel_id(DestinationShort.WALT_DISNEY_WORLD, CouchbaseChannels.CHARACTERS, "1_0", False)
    """Walt Disney World Characters Channel"""


class DLRCouchbaseChannels(str, Enum):
    FACILITIES = get_complete_channel_id(DestinationShort.DISNEYLAND_RESORT, CouchbaseChannels.FACILITIES, "1_0", True)
    """Disneyland Resort Facilities Channel"""
    FACILITY_STATUS = get_complete_channel_id(
        DestinationShort.DISNEYLAND_RESORT, CouchbaseChannels.FACILITY_STATUS, "1_0", False
    )
    """Disneyland Resort Facility Status Channel"""
    CALENDAR = get_complete_channel_id(DestinationShort.DISNEYLAND_RESORT, CouchbaseChannels.CALENDAR, "1_0", False)
    """Disneyland Resort Calendar Channel"""
    FORECASTED_WAIT_TIMES = get_complete_channel_id(
        DestinationShort.DISNEYLAND_RESORT, CouchbaseChannels.FORECASTED_WAIT_TIMES, "1_0", True
    )
    """Disneyland Resort Forecasted Wait Time Channel"""
    TODAY = get_complete_channel_id(DestinationShort.DISNEYLAND_RESORT, CouchbaseChannels.TODAY, "1_0", False)
    """Disneyland Resort Today Channel"""
    CHARACTERS = get_complete_channel_id(DestinationShort.DISNEYLAND_RESORT, CouchbaseChannels.CHARACTERS, "1_0", False)
    """Disneyland Resort Characters Channel"""


class DestinationTimezones(Enum):
    WALT_DISNEY_WORLD = ZoneInfo("America/New_York")
    """Walt Disney World Timezone"""
    DISNEYLAND_RESORT = ZoneInfo("America/Los_Angeles")
    """Disneyland Resort Timezone"""
