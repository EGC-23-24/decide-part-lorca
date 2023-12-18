from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from rest_framework_swagger.views import get_swagger_view
from authentication import views
from .views import home

urlpatterns = [
    path('', home, name='home'),
]
