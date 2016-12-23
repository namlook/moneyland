# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-13 12:54
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=20)),
                ('label', models.CharField(max_length=200)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accounts', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
            ],
            options={
                'verbose_name_plural': 'categories',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operation_date', models.DateField(verbose_name="operation date'")),
                ('value_date', models.DateField(verbose_name='value date')),
                ('label', models.CharField(max_length=255)),
                ('amount', models.FloatField(verbose_name='total amount')),
                ('num_people', models.PositiveIntegerField(default=0)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='entries.Account')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='entries.Category')),
            ],
            options={
                'verbose_name_plural': 'entries',
                'ordering': ['operation_date'],
            },
        ),
        migrations.CreateModel(
            name='ParentCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
            ],
            options={
                'verbose_name_plural': 'parent categories',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.AddField(
            model_name='entry',
            name='category_parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='entries.ParentCategory'),
        ),
        migrations.AddField(
            model_name='entry',
            name='for_people',
            field=models.ManyToManyField(related_name='entries', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='entry',
            name='paid_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='paid_entries', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='entry',
            name='supplier_found',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='entries.Supplier'),
        ),
    ]
