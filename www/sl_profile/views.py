from rest_framework.views import APIView
from rest_framework.response import Response

from . import utils

class FindAvatarKey(APIView):
    """
    Search for named avatars and return a list of matching keys
    """
    def get(self, request, name, format=None):
        keys = utils.find_avatar_key(name)
        return Response(keys)
