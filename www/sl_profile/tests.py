from uuid import UUID
import unittest

from django.test import TestCase

from sl_profile import utils

class NetworkUtilsTestCase(unittest.TestCase):
    def test_find_avatar_key(self):
        keys = utils.find_avatar_key('pippingao')
        self.assertEqual(len(keys), 1)
        self.assertEqual(keys[0], UUID('79f70eef-cb35-42a9-bfcb-3ae85acd0331'))

    def test_avatar_info(self):
        info = utils.avatar_info(UUID('79f70eef-cb35-42a9-bfcb-3ae85acd0331'))
        self.assertEqual(info.fullName, 'Pippin Gao (pippingao)')
        self.assertEqual(info.imgUrl, 'http://secondlife.com/app/image/8b1a0359-29e3-bbf0-b8eb-65af4080d2ae/1')

    def test_find_avatar_key(self):
        stores = utils.find_marketplace_store('Tapple Gao')
        self.assertEqual(len(stores), 1)
        self.assertEqual(stores[0].url, 'https://marketplace.secondlife.com/stores/62403')
        self.assertEqual(stores[0].name, 'Tavatar')

    def test_marketplace_product_info_1(self):
        info = utils.marketplace_product_info('https://marketplace.secondlife.com/p/FLG-No-Cabide-Ariana-Set-Top-Skirt-Shoes-HUDs-30-Models/11977233?ple=h')
        self.assertEqual(info.name, '::FLG No Cabide - Ariana Set -Top-Skirt-Shoes-HUDs 30 Models')
        self.assertEqual(info.imgUrl, 'https://slm-assets2.secondlife.com/assets/17458054/view_large/FLG_No_Cabide_-_Ariana_Set_-_Top_-_Skirt_-_Shoes_-_HUDs_30_Models_M.jpg?1496927352')
        self.assertEqual(info.slurl, 'http://maps.secondlife.com/secondlife/Atlantico/73/210/22')

    def test_marketplace_product_info_2(self):
        info = utils.marketplace_product_info('https://marketplace.secondlife.com/p/TentatioN-DEMO-Outfit-GUILE/8580808')
        self.assertEqual(info.name, '* TentatioN * DEMO Outfit GUILE')
        self.assertEqual(info.imgUrl, 'https://slm-assets1.secondlife.com/assets/13448064/view_large/DEMO_Outfit.jpg?1455990153')
        self.assertEqual(info.slurl, '')

class UtilsTestCase(unittest.TestCase):
    def test_to_username_1(self):
        self.assertEqual(utils.to_username('Tapple Gao'), 'tapple.gao')

    def test_to_username_2(self):
        self.assertEqual(utils.to_username('tapple.gao'), 'tapple.gao')

    def test_to_fullname_1(self):
        self.assertEqual(
                utils.to_fullname('tapple.gao', 'Tapple Gao'), 
                'Tapple Gao')

    def test_to_fullname_2(self):
        self.assertEqual(
                utils.to_fullname('tapple.gao', 'Pippin Gao'),
                'Pippin Gao (tapple.gao)')

    def test_parse_fullname_1(self):
        parsed = utils.parse_fullname('Tapple Gao')
        self.assertEqual(parsed.userName, 'tapple.gao')
        self.assertEqual(parsed.displayName, 'Tapple Gao'), 

    def test_parse_fullname_2(self):
        parsed = utils.parse_fullname('Pippin Gao (tapple.gao)')
        self.assertEqual(parsed.userName, 'tapple.gao'),
        self.assertEqual(parsed.displayName, 'Pippin Gao'),

