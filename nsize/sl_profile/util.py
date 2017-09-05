from collections import namedtuple
import re

FULLNAME_REGEX = re.compile(r'(.*) \((.*)\)')

def to_username(legacy_name):
    """ Normalizes a name to username form: lowercase, replace space with dots """
    return legacy_name.lower().replace(' ', '.')


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

# the web profiles have seperate tags for user name and display name:
# https://my.secondlife.com/tapple.gao
# The picks from that website could potentially be scraped to give folks
# a list of store slurls to choose from. It's unreliable, since picks
# are often hidden, but it's a start. The marketplace inworld store link
# is probably more useful
