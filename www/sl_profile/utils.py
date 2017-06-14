from collections import namedtuple
from urllib.parse import quote, quote_plus
from uuid import UUID
import re

import requests
from bs4 import BeautifulSoup

SL_WORLD_BASE_URL = 'http://world.secondlife.com/resident/'
SL_MARKETPLACE_BASE_URL = 'https://marketplace.secondlife.com'

def find_avatar_key(name):
    """
    Searches SL for the key of an avatar with the given name. Returns a
    list of potential UUID's
    """
    url_re = re.compile(SL_WORLD_BASE_URL + '(.*)')
    r = requests.get('http://search.secondlife.com/client_search.php?q=' + quote(name))
    soup = BeautifulSoup(r.text, "html.parser")
    tags = soup('a', href=url_re)
    return [UUID(url_re.match(tag.attrs['href']).group(1)) for tag in tags]

def avatar_info(key):
    """
    returns the (name, image url, description) of the given avatar key
    using the SL World API
    """
    Info = namedtuple("Info", 'fullName imgUrl description')
    r = requests.get(SL_WORLD_BASE_URL + str(key))
    soup = BeautifulSoup(r.text, "html.parser")
    return Info(
        soup.find('title').string,
        soup.find('img', class_='parcelimg').attrs['src'],
        soup.find('meta', attrs={'name': 'description'}).attrs['content'],
    )

def find_marketplace_store(name):
    """
    Searches SL Marketplace stores for one named name. Returns a list of
    possible results in the form of (store_url, store_name) tuples.
    Avatar username works well as name
    """
    Store = namedtuple("Store", 'url name')
    base_url = 'https://marketplace.secondlife.com'
    search_path = '/stores/store_name_search?search%5Bkeywords%5D='
    r = requests.get(base_url + search_path + quote_plus(name))
    soup = BeautifulSoup(r.text, "html.parser")
    tags = soup('a', href=re.compile('/stores/\d+'))
    return [Store(base_url + tag.attrs['href'], tag.string) for tag in tags]

def marketplace_product_info(url):
    """
    returns the (name, image url, slurl) of the marketplace product at url
    """
    Info = namedtuple("Info", 'name imgUrl slurl')
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    img_tag = soup.select_one('a#main-product-image img')
    slurl_tag = soup.select_one('a.slurl')
    slurl = ""
    if (slurl_tag): slurl = slurl_tag.attrs['href']
    return Info(
        img_tag.attrs['alt'],
        img_tag.attrs['src'],
        slurl
    )

def to_username(legacy_name):
     return legacy_name.lower().replace(' ', '.')

def parse_fullname(full_name):
    ParsedName = namedtuple("ParsedName", 'userName displayName')
    match = re.fullmatch(r'(.*) \((.*)\)', full_name)
    if (match):
        return ParsedName(match.group(2), match.group(1))
    else:
        return ParsedName(to_username(full_name), full_name)

def to_fullname(user_name, display_name):
    if (to_username(display_name) == user_name):
        return display_name
    else:
        return "%s (%s)" % (display_name, user_name)

