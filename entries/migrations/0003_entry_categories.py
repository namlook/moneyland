# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-11 09:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0002_entry_forpeople'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='categories',
            field=models.ManyToManyField(to='entries.Category'),
        ),
    ]