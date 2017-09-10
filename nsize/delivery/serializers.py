import uuid
from rest_framework import serializers

from .models import DeliveryRequest, Outfit, GarmentType, BodyPart
from sl_profile.models import Grid, Resident
from sl_profile.serializers import GridInfoSerializer
from sl_profile import util
from payroll.models import fiscal_date


class InventorySerializer(serializers.Serializer):
    key = serializers.UUIDField()
    name = serializers.CharField(max_length=64)
    """ http://wiki.secondlife.com/wiki/LlGetInventoryType """
    type = serializers.IntegerField(min_value=0, max_value=21)
    creator_key = serializers.UUIDField()
    base_perms = serializers.IntegerField()
    owner_perms = serializers.IntegerField()
    next_owner_perms = serializers.IntegerField()
    group_perms = serializers.IntegerField()
    everyone_perms = serializers.IntegerField()


class GarmentTypeSerializer(serializers.Serializer):
    id = serializers.IntegerField(min_value=0)
    name = serializers.CharField(max_length=200)


class BodyPartSerializer(serializers.Serializer):
    """ Represents a single body part """
    id = serializers.IntegerField(min_value=0)
    name = serializers.CharField(max_length=64)


class BodyPartsSerializer(serializers.Serializer):
    """ Represents a whole avatar """
    body = BodyPartSerializer()
    mods = serializers.ListField(child=BodyPartSerializer())


class OutfitServerSerializer(serializers.Serializer):
    """ Authentication information for the outfit server """
    nonce = serializers.CharField()
    signature = serializers.CharField()
    url = serializers.URLField()


class DeliveryRequestSerializer(serializers.Serializer):
    box_server_url = serializers.URLField()
    outfit_server = OutfitServerSerializer()
    body_parts = BodyPartsSerializer()
    inventory = serializers.ListField(child=InventorySerializer())
    outfit_id = serializers.UUIDField()
    creator_id = serializers.UUIDField()
    grid = GridInfoSerializer()
    outfit_components = serializers.ListField(child=GarmentTypeSerializer())

    def create(self, validated_data):
        headers = util.parse_secondlife_http_headers(validated_data['request'].META)
        instance = DeliveryRequest()
        instance.grid = Grid.get(**validated_data['grid'])
        instance.owner = Resident.get(
            grid=instance.grid,
            key=headers['owner_id'],
            name=headers['owner_name'],
        )
        instance.creator = Resident.get(
            grid=instance.grid,
            key=validated_data['creator_id'],
        )
        instance.box_id = headers['object_id']
        instance.box_name = headers['object_name']
        components = [GarmentType.objects.get(pk=type['id']) for type in validated_data['outfit_components']]
        instance.outfit, created = Outfit.objects.get_or_create(
            pk=validated_data['outfit_id'],
            defaults={
                'creator': instance.creator,
                'box_name': instance.box_name,
                'components': components,
            })
        instance.region_name = headers['region_name']
        instance.region_pos = headers['region_coordinates']
        instance.region_hostname = validated_data['grid']['region_hostname']
        instance.box_pos = headers['object_position']
        instance.box_rot = headers['object_rotation']
        instance.box_vel = headers['object_velocity']
        instance.slurl = util.slurl(headers['region_name'], headers['object_position'])
        instance.inventory_count = len(validated_data['inventory'])
        # FIXME: This is not right. Strip the inventory of internal scripts, creator prim, and notecard
        instance.extra_inventory_count = instance.inventory_count
        instance.fiscal_date = fiscal_date()
        instance.body = BodyPart.objects.get(pk=validated_data['body_parts']['body']['id'])
        instance.save()
        # Many to many relationships need primary key set first, ie, saved
        instance.mods = [BodyPart.objects.get(pk=type['id']) for type in validated_data['body_parts']['mods']]
        return instance



"""
///////////////////////////////////////////////////////////////
//////////////////////// HTTP API /////////////////////////////
///////////////////////////////////////////////////////////////

/* This script needs to implement 2-3 functions over http:

deliverOutfit(list bodyPartNames) 
Adds the garment types stored in the outfit server, then simply forwards the request to the backend as deliverGarments

runBoxCommands()
runs a sequence of the following 4 commands:
    sendItems(key dest, string folderName, list items)
wait for all the named items to be in inventory, then deliver them to the named agent or object. Used both for delivery of Creator Prim, and the delivery of the extra inventory, and possibly of parts of the outfit if an object in the region was able to send it to us
    paintItems(list items)
wait for all the named items to be painted; then we are done. This operation could easily take longer than the 30 seconds we have to send llHTTPResponse, since it involves waiting for the user to get dressed, which, worst case, requires several relogs; This  should therefore probably always be the last thing called; after finishing, we're done. Alternatively, ending this could cause a call to the server, since llHTTPResponse may have timed out
    llOwnerSay(string msg)
    llSetText(string msg, vector color, float alpha)
    llDialog(string prompt, list buttons)
This might be needed if the box is no copy; for no copy boxes, we should maybe wait for the user to positively reply. Or maybe to ask if they are using a system avatar
    done()
tells the box it's done and can, do something. For copiable boxes; there's probably nothing to do; for no-copy boxes, this is probably the place to set the "used already" flag, or delete the script, or something
    
getInventory()
replies with the inventory of the box, so the server can plan accordingly. Probably not needed; it easily fits in the deliverOutfit request (I don't expect there to be more than 8 inventory items in any box, and the base delivery request is only around 1kB
    
For maximum evolvability, This box script has almost no business logic; it is just an api for the backend server to call. This is because, once deployed, these boxes can never ever be upgraded; they will be sitting in other people's marketplace and caspervend. All the logic needs to be in the servers and garment scripts, which I can upgrade
*/




"""
