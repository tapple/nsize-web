from rest_framework.views import APIView
from rest_framework.response import Response

from . import scraper

class FindAvatarKey(APIView):
    """
    Search for named avatars and return a list of matching keys
    """
    def get(self, request, name, format=None):
        keys = scraper.find_avatar_key(name)
        return Response(keys)

class AvatarInfo(APIView):
    """
    Return full name, user name, display name, image url, description of the given uuid
    """
    def get(self, request, uuid, format=None):
        info = scraper.avatar_info(uuid)
        names = scraper.parse_fullname(info.fullName)
        #return Response({**info._asdict(), **names._asdict()}) # Only in Python 3.5+
        response = info._asdict()
        response.update(names._asdict())
        return Response(response)

class FindMarketplaceStore(APIView):
    """
    Search for the store for the given avatar name
    """
    def get(self, request, name, format=None):
        stores = scraper.find_marketplace_store(name)
        return Response([store._asdict() for store in stores])

class MarketplaceStoreInfo(APIView):
    """
    Search for the store for the given avatar name
    """
    def get(self, request, url, format=None):
        store = scraper.marketplace_store_info(url)
        return Response(store._asdict())

class MarketplaceProductInfo(APIView):
    """
    Search for the store for the given avatar name
    """
    def get(self, request, url, format=None):
        info = scraper.marketplace_product_info(url)
        return Response(info._asdict())

