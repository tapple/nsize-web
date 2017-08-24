from django.db import models

from sl_profile.models import Resident
from delivery.models import BodyPart

class CrowdSourcedField(models.Model):
    pass # no columns except primary key

""" by default, has no value. Can be used for voting """
class CrowdSourcedFieldVersion(models.Model):
    field = models.ForeignKey(CrowdSourcedField, on_delete=models.CASCADE)
    votes = models.PositiveIntegerField(default=0)
    editor_key = models.UUIDField()
    editor_ip = models.GenericIPAddressField()
    edited = models.DateTimeField(auto_now_add=True)

class CrowdSourcedCharFieldVersion(CrowdSourcedFieldVersion):
    version = models.OneToOneField(
        CrowdSourcedFieldVersion, 
        parent_link=True,
        on_delete=models.CASCADE,
        related_name='char_value',
    )
    value = models.CharField(max_length=200, blank=True)

class CrowdSourcedPositiveIntegerFieldVersion(CrowdSourcedFieldVersion):
    version = models.OneToOneField(
        CrowdSourcedFieldVersion, 
        parent_link=True,
        on_delete=models.CASCADE,
        related_name='int_value',
    )
    value = models.PositiveIntegerField(default=0)

class CrowdSourcedBooleanFieldVersion(CrowdSourcedFieldVersion):
    version = models.OneToOneField(
        CrowdSourcedFieldVersion, 
        parent_link=True,
        on_delete=models.CASCADE,
        related_name='bool_value',
    )
    value = models.BooleanField()

class LocalOrRemoteImage(models.Model):
    remote_image_url = models.URLField()
    image = models.ImageField()

    @property
    def image_url(self):
        if (self.image): return self.image.url
        else: return self.remote_image_url

    class Meta:
        abstract = True

class ResidentProfile(LocalOrRemoteImage, Resident):
    display_name = models.CharField(max_length=64)
    store_name = models.OneToOneField(
        CrowdSourcedField, 
        on_delete=models.CASCADE,
        related_name='store_name_of',
    )
    store_slurl = models.OneToOneField(
        CrowdSourcedField, 
        on_delete=models.CASCADE
        related_name='store_slurl_of',
    )
    marketplace_store_url = models.OneToOneField(
        CrowdSourcedField, 
        on_delete=models.CASCADE
        related_name='marketplace_store_url_of',
    )

class BodyPartProfile(LocalOrRemoteImage, BodyPart):
    creator = models.ForeignKey(ResidentProfile, on_delete=models.CASCADE)
    slurl = models.OneToOneField(
        CrowdSourcedField, 
        on_delete=models.CASCADE
        related_name='slurl_of',
    )
    marketplace_url = models.OneToOneField(
        CrowdSourcedField, 
        on_delete=models.CASCADE
        related_name='marketplace_url_of',
    )
    price = models.OneToOneField(
        CrowdSourcedField, 
        on_delete=models.CASCADE
        related_name='price_of',
    )

"""
People who want to be notified when new garments are made for a body part
"""
class BodyPartInterest(models.Model):
    body_part = models.ForeignKey(BodyPart, on_delete=models.CASCADE)
    resident = models.ForeignKey(Resident, on_delete=models.CASCADE)
    vote = models.BooleanField(default=False)
    watch = models.BooleanField(default=False)

class GarmentCompatibility(models.Model):
    body_part = models.ForeignKey(BodyPartProfile, on_delete=models.CASCADE)
    garment = models.ForeignKey(GarmentProfile, on_delete=models.CASCADE)
    compatible = models.OneToOneField(
        CrowdSourcedField, 
        on_delete=models.CASCADE
        related_name='compatibility_of',
    )

class GarmentProfile(LocalOrRemoteImage, Garment):
    creator = models.ForeignKey(ResidentProfile, on_delete=models.CASCADE)
    source_file = models.FileField()
    compatabilities = models.ManyToManyField(
        BodyPartProfile, 
        through=GarmentCompatibility,
        on_delete=models.CASCADE
        related_name='compatibilities',
    )



