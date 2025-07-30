# MouseTools

![PyPI - Version](https://img.shields.io/pypi/v/mousetools?style=flat-square&logo=python&color=00C106&link=https%3A%2F%2Fpypi.org%2Fproject%2Fmousetools%2F) ![PyPI - Downloads](https://img.shields.io/pypi/dm/mousetools?style=flat-square&color=blue&link=https%3A%2F%2Fpypi.org%2Fproject%2Fmousetools%2F)


An unofficial Python wrapper for the Disney API. Data is pulled directly from Disney. This package supports Walt Disney World and Disneyland Resort.

This package makes no attempt to access data that would require individual user authentication. All data is pulled using public channels.

## Installation
You can install using pip:
```bash
pip install mousetools
```
You can also install directly from this repo in case of any changes not uploaded to Pypi.
```bash
pip install git+https://gitlab.com/caratozzoloxyz/public/MouseTools
```

# Usage

The Disney API considers everything an entity. Attractions, resorts, restaurants, etc, are all entities. Entities belong to channels, or a group of entities.

## Getting Started

You'll want to create a facility channel object.

```python
from mousetools.channels.facilities import AttractionFacilityChild

pirates = AttractionFacilityChild("wdw.facilities.1_0.en_us.attraction.80010177;entityType=Attraction")
```


All Facility Entities inherit from FacilityChildChannel. 

```python
print(pirates.name)
# 'Pirates of the Caribbean'

print(pirates.ancestor_theme_park_id)
# '80007944;entityType=theme-park'
```

In order to access a facility's live data, you'll need a FacilityStatusChildChannel. Fortunately for you, this can be quickly done from the facility object.
```python
fs = pirates.get_facility_status_channel()
print(fs.get_wait_time())
# 15

print(fs.get_status())
# 'Operating'
```

Alternatively, you can create the object yourself.
```python
from mousetools.channels.facilitystatus import FacilityStatusChannel

fsc = FacilityStatusChannel("wdw.facilitystatus.1_0.80010177;entityType=Attraction", lazy_load=False)
print(fs.last_update)
# 2025-05-15 22:52:52.176069-04:00
```

***NOTE: All channels are lazy loaded, meaning there is no request sent to load the data until an object's attributes are accessed. This allows objects to be created faster, and reduce requests to Disney's servers until the data is actually needed.***


For ease of use, you can use the available channel enums or facility enums to get access to a destination facility's children channels.

```python
from mousetools.channels.facilities import FacilityChannel, ThemeParkFacilityChild
from mousetools.channel.facilities.enums import WaltDisneyWorldParkChannelIds
from mousetools.channels.facilitystatus import FacilityStatusChannel
from mousetools.channels.enums import WDWCouchbaseChannels, DLRCouchbaseChannels

wdw = FacilityChannel(WDWCouchbaseChannels.FACILITIES)
print(list(wdw.get_children_attractions()))
# [Attraction(wdw.facilities.1_0.en_us.123), Attraction(wdw.facilities.1_0.en_us.456), ...]

dlr = FacilityStatusChannel(DLRCouchbaseChannels.FACILITY_STATUS)
print(dlr.get_children_channel_ids())
# ["dlr.facilitystatus.1_0.123", "dlr.facilitystatus.1_0.456", ...]

mk = ThemeParkFacilityChild(WaltDisneyWorldParkChannelIds.MAGIC_KINGDOM, lazy_load=False)
print(mk.description)
# "Enter a Land Where Fantasy Reigns"
```

There is also a search functionality to help find the channels you want.
```python
from mousetools.api.search import Search
from mousetools.enums import DestinationShort

search = Search(DestinationShort.WALT_DISNEY_WORLD)
print(search("pirates", max_results=1))
# [{'channel_id': 'wdw.facilities.1_0.en_us.attraction.80010177;entityType=Attraction',
#   'entity_id': '80010177;entityType=Attraction',
#   'name': 'Pirates of the Caribbean',
#   'search_score': 3507.1604}]
```

### License
This project is distributed under the MIT license. For more information see [LICENSE](https://gitlab.com/caratozzoloxyz/public/MouseTools/-/blob/master/LICENSE?ref_type=heads)

### Disclaimer
This project is in no way affiliated with The Walt Disney Company and all use of Disney Services is subject to the [Disney Terms of Use](https://disneytermsofuse.com/).


### About Project

<a href='https://ko-fi.com/scaratozzolo' target='_blank'>
<img src='https://img.shields.io/badge/sponsor-30363D?style=for-the-badge&logo=kofi&logoColor=white&link=https%3A%2F%2Fko-fi.com%2Fscaratozzolo border='0' alt='Support my projects' />
</a>

MouseTools is a passion project I've been working on since 2018 when I was first learning Python. The package has evolved and been rewritten multiple times as I've become a better developer and as the Disney API has changed. There is a lot of time exploring Disney's API and figuring out how all the pieces work before any code is even written. I work on this project when I have time or when I have an idea for another project that could use this data.