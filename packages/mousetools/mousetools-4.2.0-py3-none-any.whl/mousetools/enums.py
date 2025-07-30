from enum import Enum


class DestinationShort(str, Enum):
    WALT_DISNEY_WORLD = "wdw"
    DISNEYLAND_RESORT = "dlr"


class EntityType(str, Enum):
    ATTRACTION = "Attraction"
    DINING_EVENT = "Dining-Event"
    DINNER_SHOW = "Dinner-Show"
    ENTERTAINMENT = "Entertainment"
    ENTERTAINMENT_VENUE = "Entertainment-Venue"
    EVENT = "Event"
    MERCHANDISE_FACILITY = "MerchandiseFacility"
    RECREATION = "Recreation"
    SPA = "Spa"
    AUDIO_TOUR = "audio-tour"
    BUILDING = "building"
    BUS_STOP = "bus-stop"
    DESTINATION = "destination"
    GUEST_SERVICE = "guest-service"
    LAND = "land"
    PHOTOPASS = "photopass"
    POINT_OF_INTEREST = "point-of-interest"
    RECREATION_ACTIVITY = "recreation-activity"
    RESORT = "resort"
    RESORT_AREA = "resort-area"
    RESTAURANT = "restaurant"
    THEME_PARK = "theme-park"
    TOUR = "tour"
    TRANSPORTATION = "transportation"
    WATER_PARK = "water-park"
