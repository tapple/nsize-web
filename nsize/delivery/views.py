from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import DeliveryRequest
from .serializers import DeliveryRequestSerializer


class Deliver(APIView):
    """
    Deliver an object
    """

    def post(self, request, format=None):
        serializer = DeliveryRequestSerializer(data=request.data)
        if serializer.is_valid():
            delivery_request = serializer.save(request=request)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
