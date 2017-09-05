from rest_framework import serializers


class GridSerializer(serializers.Serializer):
    """ Probably not needed """
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True, max_length=200)


class ResidentSerializer(serializers.Serializer):
    """ Probably not needed """
    id = serializers.IntegerField(read_only=True)
    key = serializers.UUIDField()
    name = serializers.CharField(max_length=64)
