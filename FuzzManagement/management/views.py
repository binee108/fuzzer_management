# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseNotAllowed
from django.conf import settings
from django.utils import timezone

from management.models import Fuzz_server
from management.models import Crash_info
from .util_func import handle_uploaded_file

from time import time
import os

# Create your views here.
# /management
def server_info(request):
    mfuzz_server = Fuzz_server.objects.all()
    template = loader.get_template('management/server_list.html')
    timedelay = timezone.now() - timezone.timedelta(minutes=30)
    context = {
        'mfuzz_server': mfuzz_server,
        'timedelay':timedelay
    }
    return HttpResponse(template.render(context, request))

# /management/connect
@csrf_exempt
def connect_ping(request):
    if not request.POST.has_key('fuzz_name'):
        return HttpResponse("Check fuzz_name.")
    if not request.POST.has_key('fuzz_ip'):
        return HttpResponse("Check fuzz_ip.")
    if not request.POST.has_key('fuzz_target'):
        return HttpResponse("Check fuzz_target.")
    if not request.POST.has_key('fuzz_version'):
        return HttpResponse("Check fuzz_version.")
    if not request.POST.has_key('working_status'):
        return HttpResponse("Check working_status.")

    try:
        mfuzz_server = Fuzz_server.objects.get(fuzz_name = request.POST['fuzz_name'])
    except:
        mfuzz_server = Fuzz_server()
    mfuzz_server.fuzz_name = request.POST['fuzz_name']
    mfuzz_server.fuzz_ip = request.POST['fuzz_ip']
    mfuzz_server.fuzz_target = request.POST['fuzz_target']
    mfuzz_server.fuzz_version = request.POST['fuzz_version']
    if request.POST['working_status']:
        mfuzz_server.last_working_time = timezone.now()
    mfuzz_server.last_connection_time = timezone.now()
    mfuzz_server.save()
    return HttpResponse("Connect Success")

# /management/crash
def crash(request):
    crash_list =  Crash_info.objects.all()
    context = {
        'mcrash_lists': crash_list
    }

    template = loader.get_template('management/crash_list.html')
    return HttpResponse(template.render(context, request))

# /management/crash_upload
@csrf_exempt
def crash_upload(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed('Use the POST method to send.')
    try :
        mfuzz = Fuzz_server.objects.get(fuzz_name = request.POST['fuzz_name'])
    except : 
        print "Check fuzz_name in fuzz_config.conf file."
        return HttpResponse('Check fuzz_name in fuzz_config.conf file.')
    
    # file save & create url
    # crash_dump = MEDIA_ROOT/crash_info/[fuzz_name]/crash_dump_[timestamp].txt
    # input_data = MEDIA_ROOT/crash_info/[fuzz_name]/input_data_[timestamp].txt
    sed =  str(int(time()*1000))
    directory = os.path.join("crash_info", request.POST['fuzz_name'])
    crash_url = directory.replace('\\','/')
    crash_dump_filename = "crash_dump_%s"%(sed) + ".txt"
    input_data_filename = "input_data_%s"%(sed) + ".txt"
    handle_uploaded_file(directory, crash_dump_filename,request.POST['crash_dump'])
    handle_uploaded_file(directory, input_data_filename,request.POST['input_data'])

    print "directory : " + directory
    print "crash_url : " + crash_url
    print "crash_dump_filename : " + crash_dump_filename
    print "input_data_filename : " + input_data_filename

    crash_dump_url = os.path.join(settings.MEDIA_URL, crash_url, crash_dump_filename).replace('\\','/')
    input_data_url = os.path.join(settings.MEDIA_URL, crash_url, input_data_filename).replace('\\','/')

    print "crash_dump_url : " + crash_dump_url
    print "input_data_url : " + input_data_url

    # Save the crash info to the DB.
    crash = Crash_info()
    crash.fuzz_server = mfuzz
    crash.crash_hash = "test_temp_data"
    crash.crash_dump = crash_dump_url
    crash.input_data = input_data_url
    crash.save()
    return HttpResponse('Upload Seccuss')


