# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-24 13:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0004_auto_20170724_1325'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModelWithFileField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('file', models.FileField(upload_to=b'')),
            ],
        ),
        migrations.DeleteModel(
            name='Document',
        ),
    ]