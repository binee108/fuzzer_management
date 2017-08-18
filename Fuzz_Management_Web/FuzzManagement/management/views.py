# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import JsonResponse
from django.utils import timezone
from django.template import loader

from management.models import Fuzzer
from management.models import Fuzz_server
from management.models import Crash_info
from management.models import Command_info
from management.models import Issue_info

from management.forms import CrashUploadForm
from management.forms import ServerMoifyForm
from management.forms import FuzzerAddForm
from management.forms import FuzzerMoifyForm
from management.forms import IssueAddForm
from management.forms import IssueModifyForm

import base64


def gentella_html(request):
    context = {}
    # The template to be loaded as per gentelella.
    # All resource paths for gentelella end in .html.

    # Pick out the html file name from the url. And load that template.
    load_template = request.path.split('/')[-1]
    template = loader.get_template('app/' + load_template)
    return HttpResponse(template.render(context, request))


# /server/list
def server_list(request):
    m_fuzz_server = Fuzz_server.objects.all()
    timedelay = timezone.now() - timezone.timedelta(seconds=60)
    context = {
        'm_fuzz_server': m_fuzz_server,
        'timedelay': timedelay
    }
    return render(request, 'management/server_list.html', context)


# /server/modify/{pk}
def server_modify(request, pk):
    m_fuzz_server = get_object_or_404(Fuzz_server, pk=pk)
    if request.method == 'POST':
        server_modify_form = ServerMoifyForm(request.POST, request.FILES, instance=m_fuzz_server)
        if server_modify_form.is_valid():
            server_save = server_modify_form.save(commit=False)
            server_save.fuzzer = Fuzzer.objects.get(id=request.POST['fuzzer_name'])
            server_save.save()
            return redirect('/server/list')
        else:
            return HttpResponseBadRequest("failed")
    else:
        fuzzers = Fuzzer.objects.all()
        m_fuzz_server = Fuzz_server.objects.get(pk=pk)
        context = {
            'm_fuzz_server': m_fuzz_server,
            'fuzzers': fuzzers
        }
        # server_modify_form = ServerMoifyForm(instance=m_fuzz_server)
        # context = {
        #     'server_modify_form': server_modify_form
        # }
        return render(request, 'management/server_modify.html', context)


def server_delete(request, pk):
    pass


# /crash_list
def crash_list(request):
    try:
        m_crash_list = Crash_info.objects.all()
    except:
        m_crash_list = []
    context = {
        'm_crash_list': m_crash_list
    }
    return render(request, 'management/crash_list.html', context)


def crash_forward(request):
    if request.method == 'POST':
        m_crash = get_object_or_404(Crash_info, pk=request.POST['crash_id'])
        m_issue = Issue_info()
        m_issue.app_name = m_crash.fuzz_server.fuzz_target
        m_issue.app_version = m_crash.fuzz_server.fuzz_version
        m_issue.regression_version = m_crash.regressions_version
        m_issue.issuer = m_crash.fuzz_server.fuzzer.fuzzer_name
        m_issue.poc_file = m_crash.test_case
        m_issue.save()
        return redirect('/crash/list')
    else:
        return HttpResponseBadRequest('Use the POST method to send.')


# /fuzzer/list
def fuzzer_list(request):
    try:
        m_fuzzers = Fuzzer.objects.all()
    except:
        m_fuzzers = []
    context = {
        'm_fuzzers': m_fuzzers
    }
    return render(request, 'management/fuzzer_list.html', context)


# /fuzzer/view/{pk}
def fuzzer_view(request, pk):
    m_fuzzer = get_object_or_404(Fuzzer, pk=pk)
    context = {
        'm_fuzzer': m_fuzzer
    }
    return render(request, 'management/fuzzer_view.html', context)
    pass


# /fuzzer/add
def fuzzer_add(request):
    if request.method == 'POST':
        fuzzer_add_form = FuzzerAddForm(request.POST, request.FILES)
        if fuzzer_add_form.is_valid():
            m_fuzzer = fuzzer_add_form.save()
            return redirect('/fuzzer/view/' + str(m_fuzzer.id))
        else:
            return redirect('/page_403.html')
    else:
        fuzzer_add_form = FuzzerAddForm()
        context = {
            'fuzzer_add_form': fuzzer_add_form
        }
        return render(request, 'management/fuzzer_add.html', context)
    pass


# /fuzzer/modify/{pk}
def fuzzer_modify(request, pk):
    m_fuzzer = get_object_or_404(Fuzzer, pk=pk)
    if request.method == 'POST':
        fuzzer_modify_form = FuzzerMoifyForm(request.POST, request.FILES, instance=m_fuzzer)
        if fuzzer_modify_form.is_valid():
            fuzzer_modify_form.save()
        return redirect('/fuzzer/view/' + str(m_fuzzer.id))
    else:
        context = {
            'm_fuzzer': m_fuzzer
        }
        # fuzzer_modify_form = FuzzerMoifyForm(instance=m_fuzzer)
        # context = {
        #     'fuzzer_modify_form': fuzzer_modify_form
        # }
        return render(request, 'management/fuzzer_modify.html', context)


def fuzzer_delete(request, pk):
    pass


def issue_list(request):
    try:
        m_issue_list = Issue_info.objects.all()
    except:
        m_issue_list = []
    context = {
        'm_issue_list': m_issue_list
    }
    return render(request, 'management/issue_list.html', context)


def issue_view(request, pk):
    m_issue = get_object_or_404(Issue_info, pk=pk)
    m_fuzz_server_list = Fuzz_server.objects.all()
    context = {
        'm_issue': m_issue,
        'm_fuzz_server_list': m_fuzz_server_list
    }
    return render(request, 'management/issue_view.html', context)
    pass


def issue_add(request):
    if request.method == 'POST':
        issue_add_form = IssueAddForm(request.POST, request.FILES)
        if issue_add_form.is_valid():
            m_issue = issue_add_form.save()
        return redirect('/issue/view/' + str(m_issue.id))
    else:
        issue_add_form = IssueAddForm()
        context = {
            'issue_add_form': issue_add_form
        }
        return render(request, 'management/issue_add.html', context)


def issue_modify(request, pk):
    m_issue = get_object_or_404(Issue_info, pk=pk)
    if request.method == 'POST':
        issue_modify_form = IssueModifyForm(request.POST, request.FILES, instance=m_issue)
        if issue_modify_form.is_valid():
            issue_modify_form.save()
            return redirect('/issue/view/' + str(m_issue.id))
        else:
            return HttpResponseBadRequest("failed")
    else:
        context = {
            'm_issue': m_issue
        }
        # issue_modify_form = IssueModifyForm(instance=m_issue)
        # context = {
        #     'issue_modify_form': issue_modify_form
        # }
        return render(request, 'management/issue_modify.html', context)


def issue_delete(request, pk):
    pass


# /manage/connect
@csrf_exempt
def connect_ping(request):
    if request.method == "POST":
        datadict = {
            'server_ip': request.POST['server_ip'],
            'last_connection_time': timezone.now()
        }
        if "On" in request.POST['working_status']:
            datadict['last_working_time'] = timezone.now()
        object_result, created = Fuzz_server.objects.update_or_create(
            pk=request.POST['server_id'],
            defaults=datadict
        )
        return HttpResponse("Connect Success")
    else:
        return HttpResponseBadRequest('Use the POST method to send.')


# /manage/register
@csrf_exempt
def register(request):
    if request.method == "POST":
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
        crash_upload_form = CrashUploadForm(request.POST, request.FILES)
        if crash_upload_form.is_valid():
            crash_save = crash_upload_form.save(commit=False)
            crash_save.fuzz_server = Fuzz_server.objects.get(id=request.POST['server_id'])
            crash_save.save()
            return HttpResponse('Upload Seccuss')
        else:
            return HttpResponseBadRequest('Upload Failed')
    else:
        return HttpResponseBadRequest('Use the POST method to send.')


# /manage/regression_version_update
@csrf_exempt
def regression_version_update(request):
    if request.method == 'POST':
        if 'issue_id' in request.POST:
            issue_id = request.POST['issue_id']
            try:
                m_issue = Issue_info.objects.get(id=issue_id)
            except:
                print "[*] - Error : issue_id is not a valid value."
                return HttpResponseBadRequest('Error : crash_id is not a valid value.')
            m_issue.regression_version = request.POST['regression_version']
            m_issue.save()
        elif "crash_id" in request.POST:
            crash_id = request.POST['crash_id']
            try:
                m_crash = Crash_info.objects.get(id=crash_id)
            except:
                print "[*] - Error : crash_id is not a valid value."
                return HttpResponseBadRequest('Error : crash_id is not a valid value.')
            m_crash.regression_version = request.POST['regression_version]']
            m_crash.save()
        else:
            print "[*] - Error : Invalid request"
            return HttpResponseBadRequest('Error : Invalid request.')
        return HttpResponse('Regression Version Update Seccuss')
    else:
        return HttpResponseBadRequest('Use the POST method to send.')


# /manage/request_command
def request_command(request):
    command_list = ['build', 'start', 'stop', 'reboot', 'regression']
    if request.method == 'POST':
        if not request.POST['command'] in command_list:
            return HttpResponseBadRequest('Invaild command.')
        else:
            m_fuzz_server = Fuzz_server.objects.get(id=request.POST['server_id'])
            m_command = Command_info()
            m_command.command = request.POST['command']
            m_command.fuzz_server = m_fuzz_server
            if 'build' in request.POST['command']:
                m_fuzzer = Fuzzer.objects.get(id=m_fuzz_server.fuzzer.id)
                buildscript_data = m_fuzzer.build_script.read()
                m_command.data = buildscript_data
            elif 'regression' in request.POST['command']:
                if 'crash_list' in request.POST['type']:
                    m_crash = Crash_info.objects.get(id=request.POST['crash_id'])
                    test_case_data = m_crash.test_case.read()
                    m_command.data = test_case_data
                    m_command.issue_id = None
                    m_command.crash_id = m_crash.id
                    m_command.save()
                    return redirect('/crash/list')
                elif 'issue' in request.POST['type']:
                    m_issue = Issue_info.objects.get(id=request.POST['issue_id'])
                    test_case_data = m_issue.poc_file.read()
                    m_command.data = test_case_data
                    m_command.issue_id = m_issue.id
                    m_command.crash_id = None
                    m_command.save()
                    return redirect('/issue/list')
                else:
                    return HttpResponseBadRequest('Invalid type')
            else:
                m_command.save()
            return redirect('/server/list')
    else:
        return HttpResponseBadRequest('Use the POST method to send.')


# /manage/command_polling
@csrf_exempt
def command_polling(request):
    if request.method == 'POST':
        try:
            m_fuzz = Fuzz_server.objects.get(id=request.POST['server_id'])
        except:
            print "Invalid access. Invalid server_name."
            return HttpResponseBadRequest('Invalid access. Check your fuzz_config.conf file.')
        try:
            m_command = Command_info.objects.filter(fuzz_server=m_fuzz).order_by('request_time')[0]
        except:
            return HttpResponse('EMPTY')
        en_data = base64.encodestring(m_command.data)
        json_data = {'command': m_command.command, 'en_data': en_data}
        if m_command.issue_id is not None:
            json_data['issue_id'] = m_command.issue_id
        elif m_command.crash_id is not None:
            json_data['crash_id'] = m_command.crash_id
        m_command.delete()
        return JsonResponse(json_data)
    else:
        return HttpResponseBadRequest('Use the POST method to send.')
