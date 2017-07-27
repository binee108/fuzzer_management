# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from .models import Fuzz_server
from .models import Crash_info

admin.site.register(Fuzz_server)
admin.site.register(Crash_info)