"""
URL configuration for nasahack project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('dowload_csv/<int:record_id>/', views.download_csv, name='download_csv'),
    path('dowload_miniseed/<int:record_id>/', views.download_miniseed, name='download_miniseed'),
    path('simulation/', views.simulation, name='simulation'),
    path('change_parameters/', views.change_parameters, name='change_parameters'),
    path('get_events/', views.get_events, name='get_events'),
]
