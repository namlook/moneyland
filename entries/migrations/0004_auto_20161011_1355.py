# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-11 13:55
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0003_entry_categories'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['title'], 'verbose_name_plural': 'categories'},
        ),
        migrations.RenameField(
            model_name='entry',
            old_name='forPeople',
            new_name='for_people',
        ),
        migrations.RenameField(
            model_name='entry',
            old_name='paidBy',
            new_name='paid_by',
        ),
    ]