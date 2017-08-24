from django.db import models
from sl_profile.models import Resident
from delivery.models import BodyPart

class BodyPartMatcher(models.Model):
    body_part = models.ForeignKey(BodyPart, on_delete=models.CASCADE)
    creator_key = models.UUIDField()
    name_matcher = models.CharField(max_length=64)
    description_matcher = models.CharField(max_length=128, default='%')
    attach_point_min = models.PositiveSmallIntegerField(default=0)
    attach_point_max = models.PositiveSmallIntegerField(default=100)

"""
Everything a person is wearing at the time of the request.
Currently not persisted
"""
class OutfitRequest(models.Model):
    owner = models.ForeignKey(Resident, on_delete=models.CASCADE)
    request_time = models.DateTimeField(auto_now_add=True)
    request_prim = models.UUIDField()
    request_slurl = models.URLField()
    corrected = models.BooleanField()
    class Meta:
        managed = False

""" Used only in the API; not persisted """
class Attachment(models.Model):
    outfit = models.ForeignKey(OutfitRequest, on_delete=models.CASCADE)
    key = models.UUIDField()
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=128)
    creator_key = models.ForeignKey(Resident, on_delete=models.CASCADE)
    attach_point = models.PositiveSmallIntegerField()
    corrected_body_part = models.ForeignKey(
        BodyPart,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    class Meta:
        managed = False

