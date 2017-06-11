
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
"""


