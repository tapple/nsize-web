# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-28 04:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Grid',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Resident',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.UUIDField()),
                ('user_name', models.CharField(db_index=True, max_length=64)),
                ('grid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sl_profile.Grid')),
            ],
        ),
        migrations.AddIndex(
            model_name='resident',
            index=models.Index(fields=['key'], name='sl_profile__key_12017a_idx'),
        ),
        migrations.AddIndex(
            model_name='resident',
            index=models.Index(fields=['user_name'], name='sl_profile__user_na_2dd07d_idx'),
        ),
    ]
