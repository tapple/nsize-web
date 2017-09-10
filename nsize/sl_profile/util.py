from collections import namedtuple
from uuid import UUID
from urllib.parse import quote
import re
import json

FULLNAME_REGEX = re.compile(r'(.*) \((.*)\)')


# Note: legacy_name cannot be reconstructed from username; the capitalization was stripped. The only way to get
# legacy name is via lsl llRequestAgentData(key, DATA_NAME)

def to_username(legacy_name):
    """
    Normalizes a name to username form: lowercase, replace space with dots:
    to_username('Tapple Gao') >>> 'tapple.gao'
    to_username('tapple.gao') >>> 'tapple.gao'
    to_username('PippinGao Resident') >>> 'pippingao'
    """
    user_name = legacy_name.lower().replace(' ', '.')
    if user_name.endswith(".resident"):
        user_name = user_name[:-9]
    return user_name


def parse_legacy_name(legacy_name):
    """
    Seperate first and last name in legacy name
    parse_legacy_name('Tapple Gao') >>> ('Tapple', 'Gao')
    parse_legacy_name('PippinGao Resident') >>> ('PippinGao', 'Resident')
    """
    ParsedName = namedtuple("ParsedName", 'first_name last_name')
    split_name = legacy_name.split(' ')
    if len(split_name) != 2:
        raise ValueError('%s is not of the form "first_name last_name"' % (legacy_name,))
    return ParsedName(*legacy_name.split(' '))


# FIXME: I wonder what happens when the display name actually ends with 'Resident'...
# I should probably actually check that this algorithm matches the viewer code.
# It's currently just reverse-engineered

def parse_fullname(full_name):
    """
    parses a full name into a user_name, display name pair:
    parse_fullname('Pippin Gao (pippingao)') >>> ('pippingao', 'Pippin Gao')
    parse_fullname('Tapple Gao') >>> ('tapple.gao', 'Tapple Gao')
    """
    ParsedName = namedtuple("ParsedName", 'user_name display_name')
    match = FULLNAME_REGEX.fullmatch(full_name)
    if match:
        return ParsedName(match.group(2), match.group(1))
    else:
        return ParsedName(to_username(full_name), full_name)


def to_fullname(user_name, display_name):
    """
    inverse of parse_fullname; combines user_name, display_name pair into a full_name
    to_fullname('pippingao', 'Pippin Gao') >>> 'Pippin Gao (pippingao)'
    to_fullname('tapple.gao', 'Tapple Gao') >>> 'Tapple Gao'
    """
    if to_username(display_name) == user_name:
        return display_name
    else:
        return "%s (%s)" % (display_name, user_name)

def slurl(region_name, position, prefix='http://maps.secondlife.com/secondlife/'):
    return '%s%s/%d/%d/%d' % (prefix, quote(region_name), position[0], position[1], position[2])

def _parse_tuple(str):
    return json.loads(str.replace('(', '[').replace(')', ']'))

def parse_secondlife_http_headers(headers):
    parsed = dict()
    parsed['owner_id'] = UUID(headers['HTTP_X_SECONDLIFE_OWNER_KEY'])
    parsed['owner_name'] = headers['HTTP_X_SECONDLIFE_OWNER_NAME']
    parsed['object_id'] = UUID(headers['HTTP_X_SECONDLIFE_OBJECT_KEY'])
    parsed['object_name'] = headers['HTTP_X_SECONDLIFE_OBJECT_NAME']
    parsed['object_position'] = _parse_tuple(headers['HTTP_X_SECONDLIFE_LOCAL_POSITION'])
    parsed['object_rotation'] = _parse_tuple(headers['HTTP_X_SECONDLIFE_LOCAL_ROTATION'])
    parsed['object_velocity'] = _parse_tuple(headers['HTTP_X_SECONDLIFE_LOCAL_VELOCITY'])
    parsed['shard'] = headers['HTTP_X_SECONDLIFE_SHARD']
    region_header = headers['HTTP_X_SECONDLIFE_REGION']
    match = FULLNAME_REGEX.fullmatch(region_header)
    parsed['region_name'] = match.group(1)
    parsed['region_coordinates'] = json.loads('[%s]' % match.group(2))
    return parsed

# the web profiles have seperate tags for user name and display name:
# https://my.secondlife.com/tapple.gao
# The picks from that website could potentially be scraped to give folks
# a list of store slurls to choose from. It's unreliable, since picks
# are often hidden, but it's a start. The marketplace inworld store link
# is probably more useful
