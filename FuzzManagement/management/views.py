# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import JsonResponse
from django.utils import timezone

from management.models import Fuzzer
from management.models import Fuzz_server
from management.models import Crash_info
from management.models import Command_info

from management.forms import CrashUploadForm
from management.forms import CommandRequestForm
from management.forms import ServerMoifyForm
import base64


# /server/list
def server_list(request):
    m_fuzz_server = Fuzz_server.objects.all()
    timedelay = timezone.now() - timezone.timedelta(minutes=30)
    context = {
        'm_fuzz_server': m_fuzz_server,
        'timedelay': timedelay
    }
    return render(request, 'management/server_list.html', context)


# /server/modify
def server_modify(request, pk):
    m_fuzz_server = get_object_or_404(Fuzz_server, pk=pk)
    if request.method == 'POST':
        server_modify_form = ServerMoifyForm(request.POST, request.FILES, instance=m_fuzz_server)
        if server_modify_form.is_valid():
            server_modify_form.save()
        else:
            print "failed"
        return redirect('/server/list')
    else:
        # m_fuzz_server = Fuzz_server.objects.get(pk=pk)
        server_modify_form = ServerMoifyForm(instance=m_fuzz_server)
        context = {
            'server_modify_form': server_modify_form
        }
        return render(request, 'management/server_modify.html', context)


def server_delete(request):
    pass


# /server/request_command
def request_command(request):
    command_list = ['setting', 'build', 'start', 'stop', 'reboot', 'regressions_search']
    if request.method == 'POST':
        if not request.POST['command'] in command_list:
            return HttpResponseBadRequest('Invaild command.')
        command_form = CommandRequestForm(request.POST, request.FILES)
        if command_form.is_valid():
            command_save = command_form.save(commit=False, fuzz_name=request.POST['fuzz_name'])
            command_save.save()
        return redirect('/server/request_command')
    else:
        m_command = Command_info.objects.all()
        command_form = CommandRequestForm()
        context = {
            'm_command': m_command,
            'command_form': command_form
        }
        return render(request, 'management/request_command.html', context)
        # return HttpResponseBadRequest('Use the POST method to send.')


def regression_search(request):
    pass


# /crash_list
def crash_list(request):
    m_crash = Crash_info.objects.all()
    context = {
        'm_crash': m_crash
    }
    return render(request, 'management/crash_list.html', context)


def fuzzer_list(request):
    try:
        m_fuzzer = Fuzzer.objects.all()
    except:
        m_fuzzer = []
    context = {
        'm_fuzzer': m_fuzzer
    }
    return render(request, 'management/fuzzer_list.html', context)


def fuzzer_view(request):
    pass


def fuzzer_add(request):
    if request.method == 'POST':
        FuzzerViewForm()
    pass


def fuzzer_modify(request, pk):
    m_fuzzer = get_object_or_404(Fuzzer, pk=pk)
    if request.method == 'POST':
        fuzzer_modify_form = FuzzerMoifyForm(request.POST, request.FILES, instance=m_fuzzer)
        if fuzzer_modify_form.is_valid():
            fuzzer_modify_form.save()
    pass


def fuzzer_delete(request):
    pass


# /manage/connect_ping
@csrf_exempt
def connect_ping(request):
    if request.method == "POST":
        datadict = {
            'fuzz_ip': request.POST['fuzz_ip'],
            'fuzz_target': request.POST['fuzz_target'],
            'fuzz_version': request.POST['fuzz_version'],
            'last_connection_time': timezone.now()
        }
        if request.POST['working_status']:
            datadict['last_working_time'] = timezone.now()
        object_result, created = Fuzz_server.objects.update_or_create(
            fuzz_name=request.POST['fuzz_name'],
            defaults=datadict
        )
        return HttpResponse("Connect Success")
    else:
        return HttpResponseBadRequest('Use the POST method to send.')


@csrf_exempt
def register(request):
    if request.method == "POST":
        print request.POST['server_id']
        if request.POST['server_id'] == "null":
            fuzz_server = Fuzz_server()
            fuzz_server.server_ip = request.POST['server_ip']
            fuzz_server.save()
            response = "server_id : " + str(fuzz_server.pk)
            return HttpResponse(response)
        else:
            return HttpResponseBadRequest('already register')


# /manage/crash_upload
@csrf_exempt
def crash_upload(request):
    if request.method == 'POST':
        try:
            m_fuzz_server = Fuzz_server.objects.get(fuzz_name=request.POST['fuzz_name'])
        except:
            return HttpResponseBadRequest('Invalid access. Check your fuzz_name in fuzz_config.conf file.')
        request.POST['fuzz_server'] = m_fuzz_server
        crash_upload_form = CrashUploadForm(request.POST, request.FILES)
        if crash_upload_form.is_valid():
            crash_save = crash_upload_form.save(commit=False, fuzz_name=request.POST['fuzz_name'])
            crash_save.save()
        return HttpResponse('Upload Seccuss')

# /manage/command_polling
@csrf_exempt
def command_polling(request):
    if request.method == 'POST':
        try:
            m_fuzz = Fuzz_server.objects.get(fuzz_name=request.POST['fuzz_name'])
        except:
            print "Invalid access. Invalid fuzz_name."
            return HttpResponseBadRequest('Invalid access. Check your fuzz_config.conf file.')
        if Command_info.objects.count() != 0:
            m_command = Command_info.objects.filter(fuzz_server=m_fuzz).order_by('request_time')[0]
            f = m_command.test_case.open(mode='rb')
            en_data = base64.encodestring(f.read())
            json_data = {'command': m_command.command, 'test_case': en_data}
            m_command.delete()
            return JsonResponse(json_data)
        else:
            return HttpResponse('EMPTY')
    else:
        return HttpResponseBadRequest('Use the POST method to send.')
