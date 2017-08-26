from django.db import models

class Grid(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.grid_name

class Resident(models.Model):
    key = models.UUIDField()
    # normalized: all lowercase, space replaced with .
    user_name = models.CharField(max_length=64, db_index=True)
    grid = models.ForeignKey(Grid, on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(fields=['key']),
            models.Index(fields=['user_name']),
        ]

    def __str__(self):
        return self.name
