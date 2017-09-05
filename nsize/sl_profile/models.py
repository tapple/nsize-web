from django.db import models
from . import util
from . import scraper


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
    def _create_secondlife_resident(cls, grid, key=None, name=None):
        """ Cache the resident by scraping the secondlife.com website """
        resident = scraper.get_resident(key=key, name=name)
        if not resident:
            raise cls.DoesNotExist
        return cls.objects.create(
            grid=grid,
            key=resident.key,
            name=util.parse_fullname(resident.full_name).user_name,
        )

    @classmethod
    def get(cls, grid, key=None, name=None):
        """
        Find a resident by key or name. Searches first in the database. If not found, screen-scrapes secondlife.com
        and stores it in the database
        """
        if name:
            name = util.to_username(name)
        # first, see if it's already in the database (fast)
        try:
            if key:
                return cls.objects.get(grid=grid, key=key)
            elif name:
                return cls.objects.get(grid=grid, name=name)
            else:
                raise ValueError('key or name must be specified')
        except cls.DoesNotExist:
            pass
        # otherwise, need to call the screen scraper
        if grid.nick in ('agni', 'aditi'):
            return cls._create_secondlife_resident(grid, key, name)
        else:
            raise NotImplementedError('Resident lookup is not implemented for grids other than Second Life')
