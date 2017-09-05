from django.db import models


class Grid(models.Model):
    name = models.CharField(max_length=200, unique=True)
    nick = models.CharField(max_length=200)
    region_domain = models.CharField(max_length=200, null=True)

    def __str__(self):
        return "name=%r, nick=%r, region_domain=%r" % (self.name, self.nick, self.region_domain)


class Resident(models.Model):
    key = models.UUIDField(db_index=True)
    # normalized: all lowercase, space replaced with .
    user_name = models.CharField(max_length=64, db_index=True)
    grid = models.ForeignKey(Grid, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
