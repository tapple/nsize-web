from uuid import UUID
import unittest

from django.test import TestCase

from .models import Grid, Resident
from . import scraper, util

NULL_KEY = UUID('00000000-0000-0000-0000-000000000000')


class ScraperTestCase(unittest.TestCase):
    def test_resident_name_search(self):
        residents = scraper.resident_name_search('pippingao')
        self.assertEqual(len(residents), 1)
        self.assertEqual(residents[0].key, UUID('79f70eef-cb35-42a9-bfcb-3ae85acd0331'))

    def test_find_by_display_name(self):
        residents = scraper.resident_name_search('Pippin Gao')
        self.assertEqual(len(residents), 1)
        self.assertEqual(residents[0].key, UUID('79f70eef-cb35-42a9-bfcb-3ae85acd0331'))

    def test_find_invalid_avatar_key(self):
        keys = scraper.resident_name_search('doesnotexist.gao')
        self.assertEqual(len(keys), 0)

    def test_resident_info(self):
        info = scraper.resident_info(UUID('79f70eef-cb35-42a9-bfcb-3ae85acd0331'))
        self.assertEqual(info.full_name, 'Pippin Gao (pippingao)')
        self.assertEqual(info.img_url, 'http://secondlife.com/app/image/8b1a0359-29e3-bbf0-b8eb-65af4080d2ae/1')

    def test_invalid_resident_info(self):
        info = scraper.resident_info(NULL_KEY)
        self.assertIsNone(info)

    def test_find_marketplace_store(self):
        stores = scraper.find_marketplace_store('Tapple Gao')
        self.assertEqual(len(stores), 1)
        self.assertEqual(stores[0].url, 'https://marketplace.secondlife.com/stores/62403')
        self.assertEqual(stores[0].name, 'Tavatar')

    @unittest.skip('switch this to a store I control. also, check that the parsing is still valid')
    def test_marketplace_store_info(self):
        store = scraper.marketplace_store_info('https://marketplace.secondlife.com/stores/185578/')
        self.assertEqual(store.name, "MAMACITA & MADUSA"),
        self.assertEqual(store.slurl, "http://maps.secondlife.com/secondlife/Coral%20Coast/217/176/3812"),
        self.assertEqual(store.legacy_name, "Y0URP0RN"),
        self.assertEqual(store.website, "http://y0urp0rn.tumblr.com/"),

    def test_marketplace_product_info_1(self):
        info = scraper.marketplace_product_info('https://marketplace.secondlife.com/p/FLG-No-Cabide-Ariana-Set-Top-Skirt-Shoes-HUDs-30-Models/11977233?ple=h')
        self.assertEqual(info.name, '::FLG No Cabide - Ariana Set -Top-Skirt-Shoes-HUDs 30 Models')
        self.assertEqual(info.img_url, 'https://slm-assets2.secondlife.com/assets/17458054/view_large/FLG_No_Cabide_-_Ariana_Set_-_Top_-_Skirt_-_Shoes_-_HUDs_30_Models_M.jpg?1496927352')
        self.assertEqual(info.slurl, 'http://maps.secondlife.com/secondlife/Atlantico/73/210/22')

    def test_marketplace_product_info_2(self):
        info = scraper.marketplace_product_info('https://marketplace.secondlife.com/p/TentatioN-DEMO-Outfit-GUILE/8580808')
        self.assertEqual(info.name, '* TentatioN * DEMO Outfit GUILE')
        self.assertEqual(info.img_url, 'https://slm-assets1.secondlife.com/assets/13448064/view_large/DEMO_Outfit.jpg?1455990153')
        self.assertEqual(info.slurl, '')


class NameParserTestCase(unittest.TestCase):
    def test_to_username_1(self):
        self.assertEqual(util.to_username('Tapple Gao'), 'tapple.gao')

    def test_to_username_2(self):
        self.assertEqual(util.to_username('tapple.gao'), 'tapple.gao')

    def test_to_username_3(self):
        self.assertEqual(util.to_username('PippinGao'), 'pippingao')

    def test_to_username_4(self):
        self.assertEqual(util.to_username('PippinGao Resident'), 'pippingao')

    def test_to_fullname_1(self):
        self.assertEqual(
                util.to_fullname('tapple.gao', 'Tapple Gao'),
                'Tapple Gao')

    def test_to_fullname_2(self):
        self.assertEqual(
                util.to_fullname('pippingao', 'Pippin Gao'),
                'Pippin Gao (pippingao)')

    def test_parse_legacy_name_1(self):
        parsed = util.parse_legacy_name('Tapple Gao')
        self.assertEqual(parsed.first_name, 'Tapple')
        self.assertEqual(parsed.last_name, 'Gao'),

    def test_parse_legacy_name_2(self):
        parsed = util.parse_legacy_name('PippinGao Resident')
        self.assertEqual(parsed.first_name, 'PippinGao')
        self.assertEqual(parsed.last_name, 'Resident'),

    def test_parse_legacy_name_3(self):
        with self.assertRaises(ValueError):
            util.parse_legacy_name('PippinGao')

    def test_parse_legacy_name_4(self):
        with self.assertRaises(ValueError):
            util.parse_legacy_name('Pippin Gao (pippin.gao)')

    def test_parse_fullname_1(self):
        parsed = util.parse_fullname('Tapple Gao')
        self.assertEqual(parsed.user_name, 'tapple.gao')
        self.assertEqual(parsed.display_name, 'Tapple Gao'),

    def test_parse_fullname_2(self):
        parsed = util.parse_fullname('Pippin Gao (tapple.gao)')
        self.assertEqual(parsed.user_name, 'tapple.gao'),
        self.assertEqual(parsed.display_name, 'Pippin Gao'),


class GetResidentTest(TestCase):
    def setUp(self):
        self.secondlife = Grid.objects.get(pk=1)
        self.tapple_key = UUID('a98362e9-bb71-45d0-aebe-3f0184f934fc')
        self.tapple_name = 'tapple.gao'
        self.tapple_legacy_name = 'Tapple Gao'
        self.tapple_first_name = 'Tapple'
        self.tapple_last_name = 'Gao'

    def create_tapple(self):
        self.assertEqual(Resident.objects.count(), 0)
        resident = Resident.objects.create(
            grid=self.secondlife,
            key=self.tapple_key,
            name=self.tapple_name,
            first_name=self.tapple_first_name,
            last_name=self.tapple_last_name,
        )
        self.assertTapple(resident)
        return resident

    def assertTapple(self, resident):
        self.assertEqual(resident.grid, self.secondlife)
        self.assertEqual(resident.key, self.tapple_key)
        self.assertEqual(resident.name, self.tapple_name)
        self.assertEqual(resident.first_name, self.tapple_first_name)
        self.assertEqual(resident.last_name, self.tapple_last_name)

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
        with self.assertRaises(Resident.DoesNotExist):
            Resident.get(self.secondlife, key=NULL_KEY)
        self.assertEqual(Resident.objects.count(), 0)

    def test_get_missing_by_invalid_name(self):
        self.assertEqual(Resident.objects.count(), 0)
        with self.assertRaises(Resident.DoesNotExist):
            Resident.get(self.secondlife, name='pippin.gao')
        self.assertEqual(Resident.objects.count(), 0)

    def test_get_missing_by_invalid_legacy_name(self):
        self.assertEqual(Resident.objects.count(), 0)
        with self.assertRaises(Resident.DoesNotExist):
            Resident.get(self.secondlife, name='Pippin Gao')
        self.assertEqual(Resident.objects.count(), 0)


class SlurlTestCase(unittest.TestCase):
    def test_slurl_1(self):
        self.assertEqual(
            util.slurl('Lost Farm', [131.02790, 84.44020, 22.80863]),
            'http://maps.secondlife.com/secondlife/Lost%20Farm/131/84/22')

