# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-13 13:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0003_auto_20161213_1350'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='supplier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='entries.Supplier'),
        ),
    ]