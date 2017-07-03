from django.conf import settings
from django.http import Http404
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
import redis

r = redis.Redis()
REDIS_PREFIX = 'lsl_gateway/cap/'

def longest_path_match(path):
    for i in range(len(path)-1, -1, -1):
        if (r.exists(REDIS_PREFIX + path[:i])):
            return path[:i], path[i:]
    return (None, None)

class MemPersistencyTest(APIView):
    """
    DEBUG: Show past requests to this django process
    """
    values = []

    def get(self, request, value, format=None):
        self.values.append(value)
        return Response(self.values)

class RegisterView(APIView):
    """
    register backend
    """
    def post(self, request, format=None):
        #import pdb; pdb.set_trace()
        r.sadd(REDIS_PREFIX + request.data['path'], request.data['url'])
        return Response(request.data)

class ProxyView(View):
    """
    register backend
    """
    def get(self, request, path, format=None):
        #import pdb; pdb.set_trace()
        base_path, proxy_path = longest_path_match(path)
        if not base_path:
            if settings.DEBUG:
                raise Http404('No caps found for path "{}". Registered paths:\n{}'
                        .format(path, r.keys(REDIS_PREFIX + "*")))
            else:
                raise Http404("Not found")
        base_url = r.srandmember(REDIS_PREFIX + base_path).decode()
        url = base_url + proxy_path
        return Response(url)
