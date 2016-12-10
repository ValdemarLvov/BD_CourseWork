from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login_user/$', views.login_user, name='login_user'),
    url(r'^register/$', views.register, name='register'),
    url(r'^logout_user/$', views.logout_user, name='logout_user'),
    url(r'^(?P<album_id>[0-9]+)/$', views.video, name='detail'),
    url(r'^my_channel/$', views.usersvideo, name='my_channel'),

]
