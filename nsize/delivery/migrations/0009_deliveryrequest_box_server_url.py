# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-10 19:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0008_auto_20170910_1911'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliveryrequest',
            name='box_server_url',
            field=models.URLField(default=''),
            preserve_default=False,
        ),
    ]
