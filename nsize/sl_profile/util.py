from collections import namedtuple
from uuid import UUID
import re


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

# the web profiles have seperate tags for user name and display name:
# https://my.secondlife.com/tapple.gao
# The picks from that website could potentially be scraped to give folks
# a list of store slurls to choose from. It's unreliable, since picks
# are often hidden, but it's a start. The marketplace inworld store link
# is probably more useful
