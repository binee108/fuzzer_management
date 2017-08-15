# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models


# Create your models here.
class Fuzzer(models.Model):
    fuzzer_name = models.CharField(max_length=100, unique=True)
    app_name = models.CharField(max_length=100)
    build_script = models.FileField(upload_to="build_script")


class Fuzz_server(models.Model):
    fuzzer = models.ForeignKey(Fuzzer, blank=True, null=True)
    server_name = models.CharField(max_length=100, blank=True, null=True)
    server_ip = models.GenericIPAddressField(blank=True, null=True)
    fuzz_target = models.CharField(max_length=100, blank=True, null=True)
    fuzz_version = models.CharField(max_length=100, blank=True, null=True)
    last_connection_time = models.DateTimeField(auto_now_add=True)
    last_working_time = models.DateTimeField(blank=True, null=True)
    # build_check = models.Boolean()


class Crash_info(models.Model):
    fuzz_server = models.ForeignKey(Fuzz_server)
    crash_hash = models.CharField(max_length=100, blank=True, null=True)
    crash_dump = models.FileField(upload_to="crash_dump")
    test_case = models.FileField(upload_to="test_case")
    crash_reliable = models.CharField(max_length=100, blank=True, null=True)
    regression_version = models.CharField(max_length=100, blank=True, null=True)
    report_time = models.DateTimeField(auto_now_add=True)


class Command_info(models.Model):
    fuzz_server = models.ForeignKey(Fuzz_server)
    issue_id = models.CharField(max_length=100, blank=True, null=True)
    crash_id = models.CharField(max_length=100, blank=True, null=True)
    command = models.CharField(max_length=100)
    data = models.TextField(blank=True)
    request_time = models.DateTimeField(auto_now_add=True)


class Issue_info(models.Model):
    app_name = models.CharField(max_length=100)
    app_version = models.CharField(max_length=100)
    regression_version = models.CharField(max_length=100, blank=True, null=True)
    issuer = models.CharField(max_length=100)
    confirmer = models.CharField(max_length=100, blank=True, null=True)
    issue_status = models.CharField(max_length=100, default="progressing")
    poc_file = models.FileField(upload_to="PoC_file")
    report_file = models.FileField(upload_to="report_file", blank=True, null=True)
    report_time = models.DateTimeField(auto_now_add=True)
