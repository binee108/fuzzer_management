# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models


# Create your models here.
class Fuzzer(models.Model):
    fuzzer_name = models.CharField(max_length=100, unique=True)
    app_name = models.CharField(max_length=100)
    build_script = models.FileField(upload_to="build_script", blank=True)


class Fuzz_server(models.Model):
    fuzzer = models.ForeignKey(Fuzzer, blank=True, null=True)
    server_name = models.CharField(max_length=100, unique=True, blank=True, null=True)
    server_ip = models.GenericIPAddressField(blank=True, null=True)
    fuzz_target = models.CharField(max_length=100, blank=True, null=True)
    fuzz_version = models.CharField(max_length=100, blank=True, null=True)
    last_connection_time = models.DateTimeField(auto_now_add=True)
    last_working_time = models.DateTimeField(blank=True, null=True)
    # build_check = models.Boolean()


class Crash_info(models.Model):
    fuzz_server = models.ForeignKey(Fuzz_server)
    crash_dump = models.FileField(upload_to="crash_dump")
    test_case = models.FileField(upload_to="test_case")
    crash_liable = models.CharField(max_length=100)
    report_time = models.DateTimeField(auto_now_add=True)
    crash_regressions_version = models.CharField(max_length=100)


class Command_info(models.Model):
    fuzz_server = models.ForeignKey(Fuzz_server)
    command = models.CharField(max_length=128)
    test_case = models.FileField(upload_to='external_issue')
    request_time = models.DateTimeField(auto_now_add=True)

    # def get_json(self):
    #     json_data = {}
    #     json_data['command'] = self.command
    #     json_data['command']

    #     return json_data
    #     pass
