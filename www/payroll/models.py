from django.db import models

from sl_profile.models import Resident
from delivery.models import Garment

class GarmentProfile(Garment):
    dae_file = models.FileField()

class GarmentDistribution(models.Model):
    garment = models.ForeignKey(GarmentProfile, on_delete=models.CASCADE)
    collaborator = models.ForeignKey(Resident, on_delete=models.CASCADE)
    percentage = models.PositiveSmallIntegerField()

