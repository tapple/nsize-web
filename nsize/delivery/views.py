from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import DeliveryRequest
from .serializers import DeliveryRequestSerializer
from . import tasks
from sl_profile import util


class Deliver(APIView):
    """
    Deliver an object
    """

    def post(self, request, format=None):
        serializer = DeliveryRequestSerializer(data=request.data)
        headers = util.parse_secondlife_http_headers(request.META)
        if serializer.is_valid():
            delivery_request = serializer.save(headers=headers)
            tasks.deliver.delay(delivery_request.id, request.data, headers)
            return Response({
                "delivery_id": delivery_request.id,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
