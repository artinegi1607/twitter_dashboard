from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^stream/', views.stream_view, name='stream'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
