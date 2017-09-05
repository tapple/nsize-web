from django.db import models


class Grid(models.Model):
    name = models.CharField(max_length=200, unique=True)
    nick = models.CharField(max_length=200)
    region_domain = models.CharField(max_length=200, null=True)

    def __str__(self):
        return "name=%r, nick=%r, region_domain=%r" % (self.name, self.nick, self.region_domain)

    @classmethod
    def get(cls, name=None, nick=None, region_hostname=None):
        """ Find the grid by name, nick, or region hostname, as these are the most accessible """
        if name:
            return cls.objects.get(name=name)
        elif nick:
            return cls.objects.get(nick=nick)
        results = list(Grid.objects.raw(
            "SELECT * FROM sl_profile_grid WHERE region_domain IS NOT NULL AND %s LIKE CONCAT('%%', region_domain)",
            [region_hostname]))
        if len(results) == 1:
            return results[0]
        elif len(results) == 0:
            raise Grid.DoesNotExist
        else:
            raise Grid.MultipleObjectsReturned


class Resident(models.Model):
    key = models.UUIDField(db_index=True)
    # normalized: all lowercase, space replaced with .
    name = models.CharField(max_length=64, db_index=True)
    grid = models.ForeignKey(Grid, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    @classmethod
    def get(cls, grid, key=None, name=None):
        from .util import get_resident # circular module dependency if declared at top
        return get_resident(grid, key, name)
