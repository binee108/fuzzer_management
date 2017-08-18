# -*- coding: utf-8 -*-
from django import forms
from management.models import Crash_info
from management.models import Fuzz_server
from management.models import Fuzzer
from management.models import Issue_info


class CrashUploadForm(forms.ModelForm):
    class Meta:
        model = Crash_info
        exclude = ['fuzz_server', 'report_time', 'regressions_version']
        fields = ['crash_dump', 'test_case', 'reliable', 'crash_hash']

    def save(self, commit=True, server_id=None):
        crash = super(CrashUploadForm, self).save(commit=False)
        if commit:
            crash.fuzz_server = Fuzz_server.objects.get(pk=server_id)
            crash.save()
        return crash


class ServerMoifyForm(forms.ModelForm):
    class Meta:
        model = Fuzz_server
        fields = ['server_name', 'fuzz_target', 'fuzz_version']
        exclude = ['fuzzer']

    def __init__(self, *args, **kwargs):
        super(ServerMoifyForm, self).__init__(*args, **kwargs)
        fuzzers = Fuzzer.objects.all()
        fuzzer_names = [(i.id, i.fuzzer_name) for i in fuzzers]
        self.fields['fuzzer_name'] = forms.ChoiceField(choices=fuzzer_names)

    # def save(self, commit=True, fuzzer_id=None):
    #     if fuzzer_id is None:
    #         return None
    #     server_modify_form = super(ServerMoifyForm, self).save(commit=False)
    #     if commit:
    #         server_modify_form.fuzzer = Fuzzer.objects.get(id=fuzzer_id)
    #         print server_modify_form.fuzzer
    #         server_modify_form.save()
    #     return server_modify_form


class FuzzerAddForm(forms.ModelForm):
    class Meta:
        model = Fuzzer
        fields = ['fuzzer_name', 'app_name', 'build_script']


class FuzzerMoifyForm(forms.ModelForm):
    class Meta:
        model = Fuzzer
        fields = ['fuzzer_name', 'app_name', 'build_script']


class IssueAddForm(forms.ModelForm):
    class Meta:
        model = Issue_info
        fields = ['app_name', 'app_version', 'issuer',
                  'poc_file', 'report_file']


class IssueModifyForm(forms.ModelForm):
    class Meta:
        model = Issue_info
        fields = ['app_name', 'app_version', 'regression_version', 'issuer',
                  'confirmer', 'issue_status', 'poc_file', 'report_file']
