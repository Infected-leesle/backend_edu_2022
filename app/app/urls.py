'''
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('django_book_app.urls')),
]'''
from django.conf.urls import url, include
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^', include('django_book_app.urls')),
]