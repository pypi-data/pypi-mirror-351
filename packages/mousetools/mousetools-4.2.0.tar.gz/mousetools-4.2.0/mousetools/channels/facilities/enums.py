from enum import Enum

from mousetools.channels.enums import DLRCouchbaseChannels, WDWCouchbaseChannels


class DestinationChannelIds(str, Enum):
    WALT_DISNEY_WORLD: str = f"{WDWCouchbaseChannels.FACILITIES.value}.destination.80007798;entityType=destination"
    """The destination id for Walt Disney World."""
    DISNEYLAND_RESORT: str = f"{DLRCouchbaseChannels.FACILITIES.value}.destination.80008297;entityType=destination"
    """The destination id for Disneyland Resort."""


class WaltDisneyWorldParkChannelIds(str, Enum):
    MAGIC_KINGDOM: str = f"{WDWCouchbaseChannels.FACILITIES.value}.theme-park.80007944;entityType=theme-park"
    """The Park id for Magic Kingdom."""
    EPCOT: str = f"{WDWCouchbaseChannels.FACILITIES.value}.theme-park.80007838;entityType=theme-park"
    """The Park id for Epcot."""
    HOLLYWOOD_STUDIOS: str = f"{WDWCouchbaseChannels.FACILITIES.value}.theme-park.80007998;entityType=theme-park"
    """The Park id for Hollywood Studios."""
    ANIMAL_KINGDOM: str = f"{WDWCouchbaseChannels.FACILITIES.value}.theme-park.80007823;entityType=theme-park"
    """The Park id for Animal Kingdom."""
    TYPHOON_LAGOON: str = f"{WDWCouchbaseChannels.FACILITIES.value}.theme-park.80007981;entityType=water-park"
    """The Park id for Typhoon Lagoon."""
    BLIZZARD_BEACH: str = f"{WDWCouchbaseChannels.FACILITIES.value}.theme-park.80007834;entityType=water-park"
    """The Park id for Blizzard Beach."""


class DisneylandResortParkChannelIds(str, Enum):
    DISNEYLAND: str = f"{DLRCouchbaseChannels.FACILITIES.value}.theme-park.330339;entityType=theme-park"
    """The Park id for Disneyland."""
    CALIFORNIA_ADVENTURE: str = f"{DLRCouchbaseChannels.FACILITIES.value}.theme-park.336894;entityType=theme-park"
    """The Park id for California Adventure."""
