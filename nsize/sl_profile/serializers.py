from rest_framework import serializers


class GridInfoSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200, required=False)
    nick = serializers.CharField(max_length=200, required=False)
    region_hostname = serializers.CharField(max_length=200)


class ResidentSerializer(serializers.Serializer):
    """ Probably not needed """
    id = serializers.IntegerField(read_only=True)
    key = serializers.UUIDField()
    name = serializers.CharField(max_length=64)
