from django.contrib import admin
from django.urls import path 
from . import views

urlpatterns = [
    path('newssubscribe',views.newssubscribe,name='newssubscribe'),
    path('newsletters',views.newsletters,name='newsletters'),
]
