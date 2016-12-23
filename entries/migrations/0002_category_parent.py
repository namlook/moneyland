# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-13 13:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='parent',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='children', to='entries.ParentCategory'),
            preserve_default=False,
        ),
    ]