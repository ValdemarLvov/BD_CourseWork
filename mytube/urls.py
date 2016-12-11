from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login_user/$', views.login_user, name='login_user'),
    url(r'^register/$', views.register, name='register'),
    url(r'^logout_user/$', views.logout_user, name='logout_user'),
    url(r'^video/(?P<id>[\w]+)/$', views.video, name='video'),
    #url(r'^(?P<video_id>[0-9]+)/$', views.video, name='video'),
#    url(r'^search/$', views.search, name='search'),
    url(r'^my_channel/$', views.usersvideo, name='my_channel'),
    url(r'^add_video/$', views.add_video, name='add video'),
    #url(r'^(?P<video_id>[0-9]+)/delete_video/$', views., name='delete_video'),
    url(r'^remove/(?P<id>[\w]+)/$', views.delete_video),
    url(r'^like/(?P<id>[\w]+)/$', views.like),
    url(r'^dislike/(?P<id>[\w]+)/$', views.dislike),
    url(r'^search/$', views.index, name='search'),
    url(r'^add_comment/(?P<id>[\w]+)/$', views.add_comment)

]
