from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^server/list$', views.server_list, name='server_list'),
    url(r'^server/modify/(?P<pk>\d+)/$', views.server_modify, name='server_modify'),

    url(r'^fuzzer/list$', views.fuzzer_list, name='fuzzer_list'),
    url(r'^fuzzer/view/(?P<pk>\d+)/$', views.fuzzer_view, name='fuzzer_view'),
    url(r'^fuzzer/add$', views.fuzzer_add, name='fuzzer_add'),
    url(r'^fuzzer/modify/(?P<pk>\d+)/$', views.fuzzer_modify, name='fuzzer_modify'),

    url(r'^issue/list$', views.issue_list, name='issue_list'),
    url(r'^issue/view/(?P<pk>\d+)/$', views.issue_view, name='issue_view'),
    url(r'^issue/add$', views.issue_add, name='issue_add'),
    url(r'^issue/modify/(?P<pk>\d+)/$', views.issue_modify, name='issue_modify'),


    url(r'^manage/register$', views.register, name='register'),
    url(r'^manage/connect$', views.connect_ping, name='connect_ping'),
    url(r'^manage/crash_upload$', views.crash_upload, name='crash_upload'),
    url(r'^manage/request_command$', views.request_command, name='request_command'),
    url(r'^manage/command_polling$', views.command_polling, name='command_polling'),
    url(r'^manage/regression_version_update$', views.regression_version_update, name='regression_version_update'),

    url(r'^crash/list$', views.crash_list, name='crash_list'),
    url(r'^crash/forward$', views.crash_forward, name='crash_forward')
]
