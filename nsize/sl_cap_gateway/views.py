import logging
from urllib.parse import unquote

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from djproxy.views import HttpProxy
from django_redis import get_redis_connection

logger = logging.getLogger(__name__)
redis = get_redis_connection("default")
REDIS_PREFIX = 'lsl_gateway/cap/'

def longest_path_match(path):
    for i in range(len(path), -1, -1):
        if (redis.exists(REDIS_PREFIX + path[:i])):
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
        logger.info("Registering cap server: %s", request.data)
        redis.sadd(REDIS_PREFIX + unquote(request.data['path']), request.data['url'])
        return Response(request.data)


@method_decorator(csrf_exempt, name='dispatch')
class ProxyView(HttpProxy):
    """
    register backend
    """

    base_url = 'ignored'

    @property
    def proxy_url(self):
        #import pdb; pdb.set_trace()
        path = self.kwargs['path']
        self.registered_path, proxy_path = longest_path_match(unquote(path))
        if not self.registered_path:
            if settings.DEBUG:
                raise KeyError('No caps found for path "{}". Registered paths:\n{}'
                        .format(path, redis.keys(REDIS_PREFIX + "*")))
            else:
                raise KeyError('No caps registered')
        self.registered_url = redis.srandmember(REDIS_PREFIX + self.registered_path).decode()
        url = self.registered_url + proxy_path
        logger.debug('Proxying request: "%s" -> "%s"', path, url)
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
                    logger.info('Cap server has disappeared: "%s" -> "%s"',
                            self.registered_path, self.registered_url)
                    redis.srem(REDIS_PREFIX + self.registered_path, self.registered_url)
        except KeyError as err:
            logger.error('No caps found for path "%s"', self.kwargs['path'])
            return HttpResponse(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                content=err.args[0])

