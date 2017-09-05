from collections import namedtuple
from urllib.parse import quote, quote_plus
from uuid import UUID
import re

import requests
import backoff
from bs4 import BeautifulSoup

from . import util

SL_WORLD_BASE_URL = 'http://world.secondlife.com/resident/'
SL_MARKETPLACE_BASE_URL = 'https://marketplace.secondlife.com'
SLURL_BASE = 'http://maps.secondlife.com/secondlife/'

SESSION = requests.Session()

@backoff.on_exception(backoff.expo,
                      (requests.exceptions.Timeout,
                       requests.exceptions.ConnectionError),
                      max_tries=3)
def get_url(url):
    r = SESSION.get(url, timeout=20)
    r.raise_for_status()
    return BeautifulSoup(r.text, "lxml")


def resident_name_search(name):
    """
    Searches SL for the key of an avatar with the given name.
    Seems to accept user names, legacy names, and display names. Returns a
    list of (uuid, full name) pairs of match results
    """
    Resident = namedtuple("Resident", 'key full_name')
    url_re = re.compile(SL_WORLD_BASE_URL + '(.*)')
    soup = get_url('http://search.secondlife.com/client_search.php?q=' + quote(name))
    tags = soup('a', href=url_re)
    return [Resident(
        UUID(url_re.match(tag.attrs['href']).group(1)),
        tag.string.strip(),
    ) for tag in tags]


def resident_info(key):
    """
    returns the (name, image url, description) of the given avatar key
    using the SL World API
    """
    ResidentInfo = namedtuple("ResidentInfo", 'key full_name img_url description')
    try:
        soup = get_url(SL_WORLD_BASE_URL + str(key))
    except requests.HTTPError as err:
        if err.response.status_code == requests.codes.not_found:
            return None
        else:
            raise
    return ResidentInfo(
        key,
        soup.find('title').string,
        soup.find('img', class_='parcelimg').attrs['src'],
        soup.find('meta', attrs={'name': 'description'}).attrs['content'],
    )


def get_resident(key=None, name=None):
    """
    look up a resident by key or username. name must be normalized to first.last form.
    Returns a tuple containing at least key and full_name
    """
    if key:
        # even if name is also given, don't trust it. Look it up
        return resident_info(key)
    elif name:
        for resident in resident_name_search(name):
            if name == util.parse_fullname(resident.full_name).user_name:
                return resident
    else:
        raise ValueError('key or name must be specified')
    return None


def find_marketplace_store(name):
    """
    Searches SL Marketplace stores for one named name. Returns a list of
    possible results in the form of (store_url, store_name) tuples.
    Avatar username works well as name
    """
    Store = namedtuple("Store", 'url name')
    base_url = 'https://marketplace.secondlife.com'
    search_path = '/stores/store_name_search?search%5Bkeywords%5D='
    soup = get_url(base_url + search_path + quote_plus(name))
    tags = soup('a', href=re.compile('/stores/\d+'))
    return [Store(base_url + tag.attrs['href'], tag.string) for tag in tags]


def marketplace_store_info(url):
    """
    returns the (name, slurl, legacy name, website, profile,
    policy) of the marketplace store at url
    """
    Store = namedtuple("Store",
                       'name slurl legacy_name, website, profile')
    r = get_url(url)
    slurl = ""
    website = ""
    for tag in r.select('a.profile-detail-link'):
        url = tag.attrs['href']
        if url.startswith(SLURL_BASE):
            slurl = url
        else:
            website = url
    return Store(
        r.select_one('div.merchant-title h5').string,
        slurl,
        r.select_one('div.merchant-title a').string,
        website,
        str(r.select_one('div.merchant-profile dl')),
    )


def marketplace_product_info(url):
    """
    returns the (name, image url, slurl) of the marketplace product at url
    """
    Info = namedtuple("Info", 'name img_url slurl')
    soup = get_url(url)
    img_tag = soup.select_one('a#main-product-image img')
    slurl_tag = soup.select_one('a.slurl')
    slurl = ""
    if (slurl_tag): slurl = slurl_tag.attrs['href']
    return Info(
        img_tag.attrs['alt'],
        img_tag.attrs['src'],
        slurl
    )


# the web profiles have seperate tags for user name and display name:
# https://my.secondlife.com/tapple.gao
# The picks from that website could potentially be scraped to give folks
# a list of store slurls to choose from. It's unreliable, since picks
# are often hidden, but it's a start. The marketplace inworld store link
# is probably more useful
