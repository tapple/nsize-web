from rest_framework import serializers


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


class GarmentType(serializers.Serializer):
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
    region_hostname = serializers.CharField()
    outfit_components = serializers.ListField(child=GarmentType())


"""
box_name = models.CharField(max_length=64)
region_name = models.CharField(max_length=32)
region_pos = fields.ArrayField(models.IntegerField(), max_length=2)
region_hostname = models.URLField(max_length=200)
box_pos = fields.ArrayField(models.FloatField(), max_length=3)
box_rot = fields.ArrayField(models.FloatField(), max_length=4)
box_vel = fields.ArrayField(models.FloatField(), max_length=3)
inventory_count = models.PositiveSmallIntegerField()
extra_inventory_count = models.PositiveSmallIntegerField()
slurl = models.URLField(max_length=200)
time = models.DateTimeField(auto_now_add=True)
grid = models.ForeignKey(Grid, on_delete=models.CASCADE)
fiscal_day = models.DateField()
"""

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
