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

class AvatarInfo(APIView):
    """
    Return full name, user name, display name, image url, description of the given uuid
    """
    def get(self, request, uuid, format=None):
        info = utils.avatar_info(uuid)
        names = utils.parse_fullname(info.fullName)
        return Response({**info._asdict(), **names._asdict()})

