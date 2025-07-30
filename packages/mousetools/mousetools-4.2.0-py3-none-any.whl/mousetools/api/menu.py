import typing
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from dateutil.parser import isoparse

from mousetools.auth import auth_obj
from mousetools.decorators import disney_property, json_property
from mousetools.mixins.disney import DisneyAPIMixin

# menus -> menu -> menugroups -> menuitems


class MenuItem:
    def __init__(self, raw_item_data: dict, parent_resturant_id: typing.Optional[str] = None):
        self._raw_item_data = raw_item_data
        self._parent_restaurant_id = parent_resturant_id

    def __repr__(self) -> str:
        return f"MenuItem(entity_id={self.entity_id}, parent_resturant_id={self._parent_restaurant_id})"

    @json_property
    def entity_id(self) -> typing.Optional[str]:
        """
        The entity id of the menu item.

        Returns:
            (typing.Optional[str]): The entity id of the menu item.
        """
        return self._raw_item_data["id"]

    @json_property
    def pc_short_name(self) -> typing.Optional[str]:
        """
        The short name of the menu item.

        Returns:
            (typing.Optional[str]): The short name of the menu item.
        """
        return self._raw_item_data["names"]["PCShort"]

    @json_property
    def pc_long_name(self) -> typing.Optional[str]:
        """
        The long name of the menu item.

        Returns:
            (typing.Optional[str]): The long name of the menu item.
        """
        return self._raw_item_data["names"]["PCLong"]

    @json_property
    def mobile_short_name(self) -> typing.Optional[str]:
        """
        The short name of the menu item.

        Returns:
            (typing.Optional[str]): The short name of the menu item.
        """
        return self._raw_item_data["names"]["MobileShort"]

    @json_property
    def mobile_long_name(self) -> typing.Optional[str]:
        """
        The long name of the menu item.

        Returns:
            (typing.Optional[str]): The long name of the menu item.
        """
        return self._raw_item_data["names"]["MobileLong"]

    @json_property
    def mickey_check(self) -> typing.Optional[bool]:
        """
        Whether the menu item is mickey check.

        Returns:
            (typing.Optional[bool]): Whether the menu item is mickey check.
        """
        return self._raw_item_data["mickeyCheck"]

    @json_property
    def pc_long_description(self) -> typing.Optional[str]:
        """
        The long description of the menu item.

        Returns:
            (typing.Optional[str]): The long description of the menu item.
        """
        return self._raw_item_data["descriptions"]["PCLong"]["text"]

    @json_property
    def mobile_short_description(self) -> typing.Optional[str]:
        """
        The short description of the menu item.

        Returns:
            (typing.Optional[str]): The short description of the menu item.
        """
        return self._raw_item_data["descriptions"]["MobileShort"]["text"]

    @json_property
    def default_selection(self) -> typing.Optional[bool]:
        """
        Whether the menu item is the default selection.

        Returns:
            (typing.Optional[bool]): Whether the menu item is the default selection.
        """
        return self._raw_item_data["defaultSelection"]

    @json_property
    def prices(self) -> typing.Optional[dict]:
        """
        The prices of the menu item.

        Returns:
            (typing.Optional[dict]): The prices of the menu item.
        """
        return self._raw_item_data["prices"]

    @json_property
    def per_serving_without_tax(self) -> typing.Optional[float]:
        """
        The per serving without tax of the menu item.

        Returns:
            (typing.Optional[float]): The per serving without tax of the menu item.
        """
        return self._raw_item_data["prices"]["PerServing"]["withoutTax"]


class MenuGroup:
    def __init__(self, raw_menu_group_data: dict, parent_restaurant_id: typing.Optional[str] = None):
        self._raw_menu_group_data = raw_menu_group_data
        self._parent_restaurant_id = parent_restaurant_id

    def __str__(self) -> str:
        return f"MenuGroup(menu_group_type={self.menu_group_type}, parent_restaurant_id={self._parent_restaurant_id})"

    @json_property
    def menu_group_type(self) -> typing.Optional[str]:
        """
        The type of the menu group.

        Returns:
            (typing.Optional[str]): The type of the menu group.
        """
        return self._raw_menu_group_data["menuGroupType"]

    @json_property
    def multiple_price_types(self) -> typing.Optional[bool]:
        """
        Whether the menu group has multiple price types.

        Returns:
            (typing.Optional[bool]): Whether the menu group has multiple price types.
        """
        return self._raw_menu_group_data["multiplePriceTypes"]

    @json_property
    def mickey_check_items(self) -> typing.Optional[bool]:
        """
        Whether the menu group has mickey check items.

        Returns:
            (typing.Optional[bool]): Whether the menu group has mickey check items.
        """
        return self._raw_menu_group_data["mickeyCheckItems"]

    @json_property
    def names(self) -> typing.Optional[dict]:
        """
        The names of the menu group.

        Returns:
            (typing.Optional[dict]): The names of the menu group.
        """
        return self._raw_menu_group_data["names"]

    @json_property
    def pc_short_name(self) -> typing.Optional[str]:
        """
        The short name of the menu group.

        Returns:
            (typing.Optional[str]): The short name of the menu group.
        """
        return self._raw_menu_group_data["names"]["PCShort"]

    @json_property
    def pc_long_name(self) -> typing.Optional[str]:
        """
        The long name of the menu group.

        Returns:
            (typing.Optional[str]): The long name of the menu group.
        """
        return self._raw_menu_group_data["names"]["PCLong"]

    @json_property
    def mobile_short_name(self) -> typing.Optional[str]:
        """
        The short name of the menu group.

        Returns:
            (typing.Optional[str]): The short name of the menu group.
        """
        return self._raw_menu_group_data["names"]["MobileShort"]

    @json_property
    def mobile_long_name(self) -> typing.Optional[str]:
        """
        The long name of the menu group.

        Returns:
            (typing.Optional[str]): The long name of the menu group.
        """
        return self._raw_menu_group_data["names"]["MobileLong"]

    @property
    def menu_items(self) -> typing.Optional[list[MenuItem]]:
        """
        The menu items of the menu group.

        Returns:
            (typing.Optional[list[MenuItem]]): The menu items of the menu group.
        """
        try:
            return [MenuItem(i, self._parent_restaurant_id) for i in self._raw_menu_group_data["menuItems"]]
        except KeyError:
            return None


class Menu:
    def __init__(self, raw_menu_data: dict, parent_restaurant_id: typing.Optional[str] = None):
        self._raw_menu_data = raw_menu_data
        self._parent_restaurant_id = parent_restaurant_id

    def __str__(self):
        return f"Menu(entity_id={self.entity_id}, menu_type={self.menu_type}, parent_restaurant_id={self._parent_restaurant_id})"

    @json_property
    def entity_id(self) -> typing.Optional[str]:
        """
        The entity id of the menu.

        Returns:
            (typing.Optional[str]): The entity id of the menu.
        """
        return self._raw_menu_data["id"]

    @json_property
    def menu_type(self) -> typing.Optional[str]:
        """
        The type of the menu.

        Returns:
            (typing.Optional[str]): The type of the menu.
        """
        return self._raw_menu_data["menuType"]

    @json_property
    def localized_menu_type(self) -> typing.Optional[str]:
        """
        The localized type of the menu.

        Returns:
            (typing.Optional[str]): The localized type of the menu.
        """
        return self._raw_menu_data["localizedMenuType"]

    @json_property
    def experience_type(self) -> typing.Optional[str]:
        """
        The experience type of the menu.

        Returns:
            (typing.Optional[str]): The experience type of the menu.
        """
        return self._raw_menu_data["experienceType"]

    @json_property
    def service_style(self) -> typing.Optional[str]:
        """
        The service style of the menu.

        Returns:
            (typing.Optional[str]): The service style of the menu.
        """
        return self._raw_menu_data["serviceStyle"]

    @json_property
    def primary_cuisine_type(self) -> typing.Optional[str]:
        """
        The primary cuisine type of the menu.

        Returns:
            (typing.Optional[str]): The primary cuisine type of the menu.
        """
        return self._raw_menu_data["primaryCuisineType"]

    @json_property
    def secondary_cuisine_type(self) -> typing.Optional[str]:
        """
        The secondary cuisine type of the menu.

        Returns:
            (typing.Optional[str]): The secondary cuisine type of the menu.
        """
        return self._raw_menu_data["secondaryCuisineType"]

    @property
    def menu_groups(self) -> list[MenuGroup]:
        """
        The menu groups of the menu.

        Returns:
            (list[MenuGroup]): The menu items of the menu.
        """
        try:
            return [MenuGroup(i, self._parent_restaurant_id) for i in self._raw_menu_data["menuGroups"]]
        except KeyError:
            return []


class Menus(DisneyAPIMixin):
    """Class for Menu Entities."""

    _menu_service_base = f"{auth_obj._environments['serviceMenuUrl']}/diningMenuSvc/orchestration/menus"

    def __init__(self, restaurant_channel_id: str, lazy_load: bool = True):
        self.entity_id = restaurant_channel_id.rsplit(".", 1)[-1]
        self._menu_service_url = f"{self._menu_service_base}/{self.entity_id}"

        self._refresh_interval: timedelta = timedelta(
            hours=12
        )  # properties are rarely updated, no need to spam the API
        self._tz = ZoneInfo("UTC")

        self._disney_data: typing.Optional[dict] = None
        self._disney_data_pull_time: datetime = datetime.now(tz=self._tz)
        if not lazy_load:
            self.refresh()

    def __str__(self):
        return f"Menus(entity_id={self.entity_id})"

    def __repr__(self):
        return f"Menus(restaurant_channel_id={self.entity_id})"

    def refresh(self) -> None:
        """Pulls initial data if none exists or if it is older than the refresh interval"""
        if self._disney_data is None or datetime.now(tz=self._tz) - self.last_refresh > self._refresh_interval:
            self._disney_data = self.get_disney_data(self._menu_service_url)
            self._disney_data_pull_time = datetime.now(tz=self._tz)

    @disney_property(default_value=[])
    def menus(self) -> list[Menu]:
        """
        Returns a list of all the menus associated with this entity.

        Returns:
            (list[Menu]): List of Menu objects that are associated with this entity.
        """

        return [Menu(i, self.entity_id) for i in self._disney_data["menus"]]

    @disney_property()
    def facility_name(self) -> typing.Optional[str]:
        """
        The name of the facility.

        Returns:
            (typing.Optional[str]): The name of the facility.
        """
        return self._disney_data["facilityName"]

    @disney_property()
    def ancestor_location_park_resort(self) -> typing.Optional[str]:
        """
        The name of the ancestor location.

        Returns:
            (typing.Optional[str]): The name of the ancestor location.
        """
        return self._disney_data["ancestorLocationParkResort"]

    @disney_property()
    def ancestor_location_land_area(self) -> typing.Optional[str]:
        """
        The name of the ancestor location.

        Returns:
            (typing.Optional[str]): The name of the ancestor location.
        """
        return self._disney_data["ancestorLocationLandArea"]

    @property
    def last_refresh(self) -> datetime:
        """
        The last time the menus were refreshed.

        Returns:
            (datetime): The last time the menus were refreshed.
        """
        if self._disney_data is None:
            self._disney_data = self.get_disney_data(self.entity_id)
        try:
            refresh_time = isoparse(self._disney_data["lastRefresh"])
            refresh_time = refresh_time.replace(tzinfo=self._tz)
            return refresh_time
        except (KeyError, TypeError, ValueError):
            return self._disney_data_pull_time
