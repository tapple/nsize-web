from rest_framework import serializers

class AttachmentSerializer(serializers.Serializer):
    pass

"""
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
"""
