from django import forms
from management.models import Crash_info
from management.models import Command_info
from management.models import Fuzz_server
from management.models import Fuzzer


class CrashUploadForm(forms.ModelForm):
    class Meta:
        model = Crash_info
        exclude = ['fuzz_server', 'report_time']
        fields = ['crash_dump', 'test_case']

    def save(self, commit=True, fuzz_name=None):
        crash = super(CrashUploadForm, self).save(commit=False)
        if commit:
            crash.fuzz_server = Fuzz_server.objects.get(fuzz_name=fuzz_name)
            crash.save()
        return crash


class CommandRequestForm(forms.ModelForm):
    class Meta:
        model = Command_info
        fields = ['command', 'test_case']
        exclude = ['fuzz_server', 'request_time']

    def __init__(self, *args, **kwargs):
        super(CommandRequestForm, self).__init__(*args, **kwargs)
        self.fields['test_case'].required = False

    def save(self, commit=True, fuzz_name=None):
        command = super(CommandRequestForm, self).save(commit=False)
        if commit:
            command.fuzz_server = Fuzz_server.objects.get(fuzz_name=fuzz_name)
            command.save()
        return command


class FuzzerViewForm(forms.ModelForm):
    class Meta:
        model = Fuzzer
        fields= ['fuzzer_name', 'app_name', 'build_script']


class ServerMoifyForm(forms.ModelForm):
    class Meta:
        model = Fuzz_server
        fields = ['fuzz', 'server_name', 'fuzz_target', 'fuzz_version']

    def __init__(self, *args, **kwargs):
        super(ServerMoifyForm, self).__init__(*args, **kwargs)
        # this is pseudo code but you should get all variants
        # then get the product related to each variant
        fuzzers = Fuzzer.objects.all()
        fuzzer_names = [(i.id, i.fuzz_name) for i in fuzzers]
        self.fields['fuzz'] = forms.ChoiceField(choices=fuzzer_names)
