# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

# Create your models here.
class Fuzz_server(models.Model):
    fuzz_name = models.CharField(max_length=100, unique=True)
    fuzz_ip = models.GenericIPAddressField()
    fuzz_target = models.CharField(max_length=100)
    fuzz_version = models.CharField(max_length=100)
    last_connection_time = models.DateTimeField(auto_now_add=True)
    working_status = models.BooleanField(default=False)

class Crash_info(models.Model):
    fuzz_server = models.ForeignKey(Fuzz_server)
    crash_hash = models.CharField(max_length=128)
    crash_dump = models.CharField(max_length=128)
    input_data = models.CharField(max_length=128)
    report_time = models.DateTimeField(auto_now_add=True)

# class ModelWithFileField(models.Model):
#     title = models.CharField(max_length=50)
#     file = models.FileField(upload_to='documens/%Y/%m/%d')