from django.db import models
import requests

from . import util
from . import scraper

# FIXME: this url should probably be a configuration thing
LSL_GATEWAY = 'http://nsize-dev.us-west-1.elasticbeanstalk.com/api/lsl_gateway/'


def get_legacy_name(grid, key):
    """ calls an in-world gateway that returns llRequestAgentData(key, DATA_NAME) """
    response = requests.get('%s/cap/%s/dataserver/llRequestAgentData/%s/2/' % (LSL_GATEWAY, grid.nick, key))
    response.raise_for_status()
    return response.text


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
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)

    def __str__(self):
        return '%s (%s)' % (self.legacy_name, self.name)

    @property
    def legacy_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    @classmethod
    def _create_secondlife_resident(cls, grid, key=None, name=None):
        """
        Cache the resident by scraping the secondlife.com website.
        name must be normalized to first.last
        """
        resident = scraper.get_resident(key=key, name=name)
        if not resident:
            raise cls.DoesNotExist
        legacy_name = get_legacy_name(grid, resident.key)
        first_name, last_name = util.parse_legacy_name(legacy_name)
        return cls.objects.create(
            grid=grid,
            key=resident.key,
            name=util.parse_fullname(resident.full_name).user_name,
            first_name=first_name,
            last_name=last_name,
        )

    @classmethod
    def get(cls, grid, key=None, name=None):
        """
        Find a resident by key or name. Searches first in the database. If not found, screen-scrapes secondlife.com
        and stores it in the database. name can be in either username or legacy form, if given
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
