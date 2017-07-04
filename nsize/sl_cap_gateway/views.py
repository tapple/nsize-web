from django.conf import settings
from django.http import HttpResponse

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from djproxy.views import HttpProxy
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

class ProxyView(HttpProxy):
    """
    register backend
    """

    base_url = 'ignored'

    @property
    def proxy_url(self):
        #import pdb; pdb.set_trace()
        path = self.kwargs['path']
        self.registered_path, proxy_path = longest_path_match(path)
        if not self.registered_path:
            if settings.DEBUG:
                raise KeyError('No caps found for path "{}". Registered paths:\n{}'
                        .format(path, r.keys(REDIS_PREFIX + "*")))
            else:
                raise KeyError('No caps registered')
        self.registered_url = r.srandmember(REDIS_PREFIX + self.registered_path).decode()
        url = self.registered_url + proxy_path
        print('"{}" + "{}"'.format(self.registered_url, proxy_path))
        return url

    def is_healthy(self, response):
        if (response.status_code != status.HTTP_404_NOT_FOUND): return True
        if (not response.content.startswith(b"cap not found: ")): return True
        return False

    def proxy(self):
        try:
            while True:
                response = super().proxy()
                #import pdb; pdb.set_trace()
                if (self.is_healthy(response)):
                    return response
                else:
                    r.srem(REDIS_PREFIX + self.registered_path, self.registered_url)
        except KeyError as err:
            return HttpResponse(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                content=err.args[0])

