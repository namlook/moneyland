# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-15 12:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0007_auto_20161215_1212'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='slug',
            field=models.SlugField(default='', max_length=200, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='parentcategory',
            name='slug',
            field=models.SlugField(default=' ', max_length=200, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='supplier',
            name='slug',
            field=models.SlugField(default='.', max_length=200, unique=True),
            preserve_default=False,
        ),
    ]
