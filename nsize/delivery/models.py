from django.db import models
from django.contrib.postgres import fields

from sl_profile.models import Grid, Resident


class BodyPart(models.Model):
    name = models.CharField(max_length=64, unique=True, db_index=True)
    modifies = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='mods',
        related_query_name='mod',
        null=True,
    )

    def __str__(self):
        return self.name


class GarmentType(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class BodySpec(models.Model):
    body = models.ForeignKey(
        BodyPart,
        on_delete=models.CASCADE,
    )
    mods = models.ManyToManyField(
        BodyPart,
        related_name='+',
    )

    class Meta:
        abstract = True


class Garment(BodySpec):
    type = models.ForeignKey(GarmentType, on_delete=models.CASCADE)

    date_added = models.DateField(auto_now_add=True)
    date_removed = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.type_name


class GarmentAsset(models.Model):
    garment = models.ForeignKey(
        Garment,
        on_delete=models.CASCADE,
        related_name='assets',
        related_query_name='asset',
    )
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Outfit(models.Model):
    """
    Every outfit that a texture artist makes. Currently only used for
    auditing sellers who aren't distributing enough to nSize. Due to that,
    this table is only maintained once per day, during the daily settlement
    """
    id = models.UUIDField(primary_key=True)
    creator = models.ForeignKey(Resident, on_delete=models.CASCADE)
    first_seen_time = models.DateTimeField(auto_now_add=True)
    # box name might change without changing outfit id, but probably not after
    # being sold. Just in case, update the box_name each day the outfit is seen
    box_name = models.CharField(max_length=64)
    components = models.ManyToManyField(GarmentType)


class DeliveryRequest(BodySpec):
    outfit = models.ForeignKey(
        Outfit,
        on_delete=models.CASCADE,
        related_name='+',
    )
    """ creator is a duplicate of outfit.creator, but is kept because its indexed """
    creator = models.ForeignKey(
        Resident,
        on_delete=models.CASCADE,
        related_name='+',
    )
    owner = models.ForeignKey(
        Resident,
        on_delete=models.CASCADE,
        related_name='+',
    )
    box_id = models.UUIDField()
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
    fiscal_date = models.DateField()

    class Meta:
        db_table = 'delivery_request_log'
        indexes = [
            models.Index(fields=['grid', 'fiscal_date', 'creator']),
            models.Index(fields=['grid', 'creator', 'fiscal_date']),
        ]
