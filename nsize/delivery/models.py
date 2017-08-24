from django.db import models

class BodyPart(models.Model):
    name = models.CharField(max_length=64, unique=True, db_index=True)
    modifies = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE,
        related_name='mods',
        related_query_name='mod',
    )

    def __str__(self):
        return self.question_text

class GarmentType(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Garment(models.Model):
    type = models.ForeignKey(GarmentType, on_delete=models.CASCADE)
    avatar = models.ForeignKey(
        BodyPart, 
        on_delete=models.CASCADE,
        related_name='avatar_garments',
        related_query_name='avatar_garment',
    )
    mods = models.ManyToManyField(
        BodyPart,
        related_name='mod_garments',
        related_query_name='mod_garment',
    )

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

