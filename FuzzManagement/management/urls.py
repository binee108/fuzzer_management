from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.server_info, name='server_info'),
    url(r'^connect$', views.connect_ping, name='connect_ping'),
    url(r'^crash$', views.crash, name='crash'),
    url(r'^crash_upload$', views.crash_upload, name='crash_upload')
]
