from rest_framework.views import APIView
from rest_framework.response import Response

class MemPersistencyTest(APIView):
    """
    DEBUG: Show past requests to this django process
    """
    values = []

    def get(self, request, value, format=None):
        self.values.append(value)
        return Response(self.values)
