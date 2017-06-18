from django.db import models
from delivery.models import BodyPart

class Attachment(models.Model):
    key = models.UUIDField()
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=128)
    creator_key = models.UUIDField()
    attach_point = models.PositiveSmallIntegerField()

class BodyPartMatcher(models.Model):
    body_part = models.ForeignKey(BodyPart, on_delete=models.CASCADE)
    creator_key = models.UUIDField()
    name_matcher = models.CharField(max_length=64)
    description_matcher = models.CharField(max_length=128, default='%')
    attach_point_min = models.PositiveSmallIntegerField(default=0)
    attach_point_max = models.PositiveSmallIntegerField(default=100)

