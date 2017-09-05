from uuid import UUID
import unittest

from django.test import TestCase

from .models import Grid, Resident
from . import scraper

NULL_KEY = UUID('00000000-0000-0000-0000-000000000000')

class ScraperTestCase(unittest.TestCase):
    def test_find_avatar_key(self):
        keys = scraper.find_avatar_key('pippingao')
        self.assertEqual(len(keys), 1)
        self.assertEqual(keys[0], UUID('79f70eef-cb35-42a9-bfcb-3ae85acd0331'))

    def test_find_invalid_avatar_key(self):
        keys = scraper.find_avatar_key('pipppin.gao')
        self.assertEqual(len(keys), 0)

    def test_avatar_info(self):
        info = scraper.avatar_info(UUID('79f70eef-cb35-42a9-bfcb-3ae85acd0331'))
        self.assertEqual(info.fullName, 'Pippin Gao (pippingao)')
        self.assertEqual(info.imgUrl, 'http://secondlife.com/app/image/8b1a0359-29e3-bbf0-b8eb-65af4080d2ae/1')

    def test_invalid_avatar_info(self):
        info = scraper.avatar_info(NULL_KEY)
        self.assertIsNone(info)

    def test_find_marketplace_store(self):
        stores = scraper.find_marketplace_store('Tapple Gao')
        self.assertEqual(len(stores), 1)
        self.assertEqual(stores[0].url, 'https://marketplace.secondlife.com/stores/62403')
        self.assertEqual(stores[0].name, 'Tavatar')

    def test_marketplace_store_info(self):
        store = scraper.marketplace_store_info('https://marketplace.secondlife.com/stores/185578/')
        self.assertEqual(store.name, "MAMACITA & MADUSA"),
        self.assertEqual(store.slurl, "http://maps.secondlife.com/secondlife/Coral%20Coast/217/176/3812"),
        self.assertEqual(store.legacyName, "Y0URP0RN"),
        self.assertEqual(store.website, "http://y0urp0rn.tumblr.com/"),

    def test_marketplace_product_info_1(self):
        info = scraper.marketplace_product_info('https://marketplace.secondlife.com/p/FLG-No-Cabide-Ariana-Set-Top-Skirt-Shoes-HUDs-30-Models/11977233?ple=h')
        self.assertEqual(info.name, '::FLG No Cabide - Ariana Set -Top-Skirt-Shoes-HUDs 30 Models')
        self.assertEqual(info.imgUrl, 'https://slm-assets2.secondlife.com/assets/17458054/view_large/FLG_No_Cabide_-_Ariana_Set_-_Top_-_Skirt_-_Shoes_-_HUDs_30_Models_M.jpg?1496927352')
        self.assertEqual(info.slurl, 'http://maps.secondlife.com/secondlife/Atlantico/73/210/22')

    def test_marketplace_product_info_2(self):
        info = scraper.marketplace_product_info('https://marketplace.secondlife.com/p/TentatioN-DEMO-Outfit-GUILE/8580808')
        self.assertEqual(info.name, '* TentatioN * DEMO Outfit GUILE')
        self.assertEqual(info.imgUrl, 'https://slm-assets1.secondlife.com/assets/13448064/view_large/DEMO_Outfit.jpg?1455990153')
        self.assertEqual(info.slurl, '')


class NameParserTestCase(unittest.TestCase):
    def test_to_username_1(self):
        self.assertEqual(scraper.to_username('Tapple Gao'), 'tapple.gao')

    def test_to_username_2(self):
        self.assertEqual(scraper.to_username('tapple.gao'), 'tapple.gao')

    def test_to_fullname_1(self):
        self.assertEqual(
                scraper.to_fullname('tapple.gao', 'Tapple Gao'),
                'Tapple Gao')

    def test_to_fullname_2(self):
        self.assertEqual(
                scraper.to_fullname('tapple.gao', 'Pippin Gao'),
                'Pippin Gao (tapple.gao)')

    def test_parse_fullname_1(self):
        parsed = scraper.parse_fullname('Tapple Gao')
        self.assertEqual(parsed.userName, 'tapple.gao')
        self.assertEqual(parsed.displayName, 'Tapple Gao'),

    def test_parse_fullname_2(self):
        parsed = scraper.parse_fullname('Pippin Gao (tapple.gao)')
        self.assertEqual(parsed.userName, 'tapple.gao'),
        self.assertEqual(parsed.displayName, 'Pippin Gao'),


class GetResidentTest(TestCase):
    def setUp(self):
        self.secondlife = Grid.objects.get(pk=1)
        self.tapple_key = UUID('a98362e9-bb71-45d0-aebe-3f0184f934fc')
        self.tapple_name = 'tapple.gao'
        self.tapple_legacy_name = 'Tapple Gao'

    def create_tapple(self):
        self.assertEqual(Resident.objects.count(), 0)
        return Resident.objects.create(grid=self.secondlife, key=self.tapple_key, name=self.tapple_name)

    def assertTapple(self, resident):
        self.assertEqual(resident.grid, self.secondlife)
        self.assertEqual(resident.key, self.tapple_key)
        self.assertEqual(resident.name, self.tapple_name)

    def test_get_present_by_valid_key(self):
        tapple = self.create_tapple()
        self.assertEqual(Resident.get(self.secondlife, key=self.tapple_key), tapple)
        self.assertEqual(Resident.objects.count(), 1)

    def test_get_present_by_valid_name(self):
        tapple = self.create_tapple()
        self.assertEqual(Resident.get(self.secondlife, name=self.tapple_name), tapple)
        self.assertEqual(Resident.objects.count(), 1)

    def test_get_present_by_valid_legacy_name(self):
        tapple = self.create_tapple()
        self.assertEqual(Resident.get(self.secondlife, name=self.tapple_legacy_name), tapple)
        self.assertEqual(Resident.objects.count(), 1)

    def test_get_missing_by_valid_key(self):
        self.assertEqual(Resident.objects.count(), 0)
        resident = Resident.get(self.secondlife, key=self.tapple_key)
        self.assertTapple(resident)
        self.assertEqual(Resident.objects.count(), 1)
        self.assertEqual(Resident.objects.all()[0], resident)

    def test_get_missing_by_valid_name(self):
        self.assertEqual(Resident.objects.count(), 0)
        resident = Resident.get(self.secondlife, name=self.tapple_name)
        self.assertTapple(resident)
        self.assertEqual(Resident.objects.count(), 1)
        self.assertEqual(Resident.objects.all()[0], resident)

    def test_get_missing_by_valid_legacy_name(self):
        self.assertEqual(Resident.objects.count(), 0)
        resident = Resident.get(self.secondlife, name=self.tapple_legacy_name)
        self.assertTapple(resident)
        self.assertEqual(Resident.objects.count(), 1)
        self.assertEqual(Resident.objects.all()[0], resident)

    def test_get_missing_by_invalid_key(self):
        self.assertEqual(Resident.objects.count(), 0)
        self.assertRaises(Resident.get(self.secondlife, key=NULL_KEY), Resident.DoesNotExist)
        self.assertEqual(Resident.objects.count(), 0)

    def test_get_missing_by_invalid_name(self):
        self.assertEqual(Resident.objects.count(), 0)
        self.assertRaises(Resident.get(self.secondlife, name='pippin.gao'), Resident.DoesNotExist)
        self.assertEqual(Resident.objects.count(), 0)

    def test_get_missing_by_invalid_legacy_name(self):
        self.assertEqual(Resident.objects.count(), 0)
        self.assertRaises(Resident.get(self.secondlife, name='Pippin Gao'), Resident.DoesNotExist)
        self.assertEqual(Resident.objects.count(), 0)


