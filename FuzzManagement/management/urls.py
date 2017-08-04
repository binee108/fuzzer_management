from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^server/list$', views.server_list, name='server_list'),
    url(r'^server/modify/(?P<pk>\d+)/$', views.server_modify, name='server_modify'),
    url(r'^server/request_command$', views.request_command, name='request_command'),
    url(r'^fuzzer/list$', views.fuzzer_list, name='fuzzer_list'),
    url(r'^fuzzer/modify/(?P<pk>\d+)/$', views.fuzzer_modify, name='fuzzer_modify'),
    url(r'^manage/connect$', views.connect_ping, name='connect_ping'),
    url(r'^manage/crash_upload$', views.crash_upload, name='crash_upload'),
    url(r'^manage/command_polling$', views.command_polling, name='command_polling'),
    url(r'^crash/list$', views.crash_list, name='crash_list'),
    url(r'^register$', views.register, name='register')
]
