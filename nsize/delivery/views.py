from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import DeliveryRequest
from .serializers import DeliveryRequestSerializer
from . import tasks


class Deliver(APIView):
    """
    Deliver an object
    """

    def post(self, request, format=None):
        serializer = DeliveryRequestSerializer(data=request.data)
        if serializer.is_valid():
            delivery_request = serializer.save(request=request)
            tasks.instant_message.delay(delivery_request.owner.key, "hello from django celery")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
