from django.db import models

from sl_profile.models import Resident
from delivery.models import BodyPart

class ResidentProfile(Resident):
    store_slurl = models.URLField()
    marketplace_url = models.URLField()
    image = models.ImageField()
    prev_version = models.OneToOneField('self', on_delete=models.CASCADE)
    modified = models.DateTimeField(auto_now=True)

class BodyPartProfile(BodyPart):
    creator = models.ForeignKey(ResidentProfile, on_delete=models.CASCADE)
    store_slurl = models.URLField()
    marketplace_url = models.URLField()
    image = models.ImageField()
    modified = models.DateTimeField(auto_now=True)

