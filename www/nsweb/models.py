from django.db import models

from sl_profile.models import Resident
from delivery.models import BodyPart

class LocalOrRemoteImage(models.Model):
    remote_image_url = models.URLField()
    image = models.ImageField()

    @property
    def image_url(self):
        if (self.image): return self.image.url
        else: return self.remote_image_url

    class Meta:
        abstract = True

class TrackModification(models.Model):
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class ResidentProfile(TrackModification, LocalOrRemoteImage, Resident):
    display_name = models.CharField(max_length=64)
    store_name = models.CharField(max_length=200)
    store_slurl = models.URLField()
    marketplace_url = models.URLField()

class BodyPartProfile(TrackModification, LocalOrRemoteImage, BodyPart):
    creator = models.ForeignKey(ResidentProfile, on_delete=models.CASCADE)
    store_slurl = models.URLField()
    marketplace_url = models.URLField()
    modified = models.DateTimeField(auto_now=True)

