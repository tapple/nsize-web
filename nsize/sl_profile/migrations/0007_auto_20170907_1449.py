# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-07 14:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sl_profile', '0006_auto_20170905_0625'),
    ]

    operations = [
        migrations.AddField(
            model_name='resident',
            name='first_name',
            field=models.CharField(default='', max_length=64),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='resident',
            name='last_name',
            field=models.CharField(default='', max_length=64),
            preserve_default=False,
        ),
    ]
