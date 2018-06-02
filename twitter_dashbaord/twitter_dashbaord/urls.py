from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views

from tweet.views import ErrorView


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^auth/', include('social_django.urls', namespace='social')),
    url(r'^tweet/', include('tweet.urls', namespace='tweet')),
    url(r'^error-page/$', ErrorView.as_view(), name="error_page"),
    url(r'^$', views.login, name='index'),
]
