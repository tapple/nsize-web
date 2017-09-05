from collections import namedtuple
from uuid import UUID
import re

from .models import Resident
from .scraper import find_avatar_key, avatar_info


def to_username(legacy_name):
    return legacy_name.lower().replace(' ', '.')


def parse_fullname(full_name):
    ParsedName = namedtuple("ParsedName", 'userName displayName')
    match = re.fullmatch(r'(.*) \((.*)\)', full_name)
    if match:
        return ParsedName(match.group(2), match.group(1))
    else:
        return ParsedName(to_username(full_name), full_name)


def to_fullname(user_name, display_name):
    if to_username(display_name) == user_name:
        return display_name
    else:
        return "%s (%s)" % (display_name, user_name)


def get_resident(grid, key=None, name=None):
    """
    Find a resident by key or name. Searches first in the database. If not found, screen-scrapes secondlife.com
    and stores it in the database
    """
    if name:
        name = to_username(name)

    # first, see if it's already in the database (fast)
    try:
        if key:
            return Resident.objects.get(grid=grid, key=key)
        elif name:
            return Resident.objects.get(grid=grid, name=name)
        else:
            raise ValueError('key or name must be specified')
    except Resident.DoesNotExist:
        pass

    # otherwise, need to call the screen scraper
    if grid.nick in ('agni', 'aditi'):
        return _create_second_life_resident(grid, key=key, name=name)
    else:
        raise NotImplementedError('Resident lookup is unimplemented for grids other than Second Life')


def _create_second_life_resident(grid, key=None, name=None):
    if key:
        # even if name is also given, don't trust it. Look it up
        info = avatar_info(key)
        if info:
            (name, display_name) = parse_fullname(info.full_name)
            # FIXME: maybe cache the display name
        else:
            raise Resident.DoesNotExist
    elif name:
        keys = find_avatar_key(name)
        if len(keys) == 1:
            key = keys[0]
        elif len(keys) == 0:
            raise Resident.DoesNotExist
        else:
            raise Resident.MultipleObjectsReturned
    return Resident.objects.create(grid=grid, key=key, name=name)


# the web profiles have seperate tags for user name and display name:
# https://my.secondlife.com/tapple.gao
# The picks from that website could potentially be scraped to give folks
# a list of store slurls to choose from. It's unreliable, since picks
# are often hidden, but it's a start. The marketplace inworld store link
# is probably more useful
