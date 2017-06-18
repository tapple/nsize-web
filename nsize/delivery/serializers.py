
"""
class ExtraInventoryItem(models.Model):
    key = models.UUIDField()
    name = models.CharField(max_length=64)
    type = models.PositiveSmallIntegerField()
    creator_key = models.UUIDField()
    base_perms = models.IntegerField()
    owner_perms = models.IntegerField()
    next_owner_perms = models.IntegerField()
    group_perms = models.IntegerField()
    everyone_perms = models.IntegerField()

    def __str__(self):
        return self.name

class DeliveryRequest(models.Model):
    session_id = models.UUIDField()
    owner_id = models.UUIDField()
    outfit_id = models.UUIDField()
    prim_id = models.UUIDField()
    prim_name = models.CharField(max_length=64)
    prim_url = models.URLField()
    prim_pos = models.CharField()
    region_name = models.CharField(max_length=64)
    region_hostname = models.URLField()
    outfit_url = models.URLField()
    outfit_nonce = models.IntegerField()

    def __str__(self):
        return self.name

///////////////////////////////////////////////////////////////
///////////////////// Data Gathering //////////////////////////
///////////////////////////////////////////////////////////////

//*
// As of 2017-06-13, up to 38 attachments can be worn per agent
// max of 328 bytes per attach point (if name and description are maxed out).
//     x38 = 12464 bytes
// without descriptions: 188 * 38 = 7144 bytes top
// I measured a real outfit with 38 attachments; it's json encoding was 6877 bytes
string avatarAttachmentsJson(key id) {
    list ans = [];
    list attachments = llGetAttachedList(id);
debug((string)llGetListLength(attachments) + " attachments");
    integer i;
    for (i = llGetListLength(attachments) - 1; i >= 0; i--) {
        key attachment = llList2Key(attachments, i);
        list details = llGetObjectDetails(attachment, [OBJECT_NAME, OBJECT_DESC, OBJECT_CREATOR, OBJECT_ATTACHED_POINT]);
        ans = [llList2Json(JSON_OBJECT, [
            "id", attachment, // 6+2+36 = 44 bytes
            "name", llList2String(details, 0), // 6+4+64 = 74 bytes
            "desc", llList2String(details, 1), // 6+4+128 = 140 bytes
            "creator", llList2String(details, 2), // 6+7+36 = 49 bytes
            "attachPoint", llList2String(details, 3) // 6+11+2 = 19 bytes
        ])] + ans;
    }
    return llList2Json(JSON_ARRAY, ans);
}

// 310 bytes per inventory item with all perms (33 items in 10kB)
// 207 bytes per item with only base perms (49 items in 10kB)
// 110 bytes per item with only name, type, perms (93 items in 10kB)
string extraInventoryJson() {
//    list exceptions = [llGetScriptName(), NOTECARD_NAME, CREATOR_PRIM];
    list inv = [];
    integer i;
    for (i = llGetInventoryNumber(INVENTORY_ALL)-1; i >= 0; --i) {
        string item = llGetInventoryName(INVENTORY_ALL, i);
        inv = [llList2Json(JSON_OBJECT, [
            "key", llGetInventoryKey(item), // 6+3+36 = 45 bytes
            "name", item, // 6+4+64 = 74 bytes
            "type", llGetInventoryType(item), // 6+4+2 = 12 bytes
            "creatorKey", llGetInventoryCreator(item), // 6+10+36 = 52 bytes
            "basePerms", llGetInventoryPermMask(item, MASK_BASE), // 4+9+10 = 23
            "ownerPerms", llGetInventoryPermMask(item, MASK_OWNER), // 4+10+10 = 24
            "nextOwnerPerms", llGetInventoryPermMask(item, MASK_NEXT), // 4+14+10 = 28
            "groupPerms", llGetInventoryPermMask(item, MASK_GROUP), // 4+10+10 = 24
            "everyonePerms", llGetInventoryPermMask(item, MASK_EVERYONE) // 4+13+10 = 27
            //"dataKey", llRequestInventoryData(item), // 1 second delay to get landmark dest
        ])] + inv;
    }
    return llList2Json(JSON_ARRAY, inv);
}

string mainServerRequest() {
    vector pos = llGetPos();
    list request = [
        "sessionId", sessionId,
        "outfitId", outfitId,
        "primId", llGetKey(),
        "primName", llGetObjectName(),
        "primUrl", url,
        "primPos", llList2Json(JSON_ARRAY, [pos.x, pos.y, pos.z]),
        "regionName", llGetRegionName(),
        "regionHostname", llGetEnv("simulator_hostname"),
//        "hasCreatorPrim", llGetInventoryType(CREATOR_PRIM) == INVENTORY_OBJECT,
/* Not sure yet if these should be set by the box or the server
        "outfitFolderName", llGetObjectName() + " (Outfit)",
        "extrasFolderName", llGetObjectName() + " (Extras)",
        "fullFolderName", llGetObjectName(),
//*/
//        "avatarAttachments", avatarAttachmentsJson(llGetOwner()),
        "extraInventory", extraInventoryJson()
    ];
    request += ["outfitComponents", "[]"];
    if (SHOULD_SEND_TEXTURES) {
        request += ["outfitUrlKey", ""];
    }
    return llList2Json(JSON_OBJECT, request);
}

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



