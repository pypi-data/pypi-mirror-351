from mousetools.auth import auth_obj
from mousetools.mixins.couchbase import CouchbaseMixin
from mousetools.mixins.disney import DisneyAPIMixin


def test_couchbase_mixin():
    cb = CouchbaseMixin()
    channel_data = cb.get_channel_data("wdw.facilities.1_0.en_us.attraction.80010177;entityType=Attraction")
    channel_changes = cb.get_channel_changes("wdw.facilities.1_0.en_us")

    assert channel_data

    assert channel_changes
    assert len(channel_changes["results"]) > 0

    channel_data = cb.get_channel_data("wdw.notreal.1_0")
    assert channel_data.get("error", "") == "not_found"

    cb._couchbase_url = "http://notreal.com"
    channel_data = cb.get_channel_data("wdw.facilities.1_0.en_us.attraction.80010177;entityType=Attraction")
    channel_changes = cb.get_channel_changes("wdw.facilities.1_0.en_us", since=3900000)
    assert channel_data is None
    assert channel_changes is None


def test_disney_mixin():
    disney = DisneyAPIMixin()
    data = disney.get_disney_data(
        f"{auth_obj._environments['serviceMenuUrl']}/diningMenuSvc/orchestration/menus/17936197"
    )

    assert data
    assert "menus" in data

    data = disney.get_disney_data("http://notreal.com")

    assert data is None
