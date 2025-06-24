from django.urls import path
from . import views

urlpatterns = [
    path('api/home_feed/', views.home_feed, name='home_feed'),
    path('api/trigger_scraping/', views.trigger_scraping, name='trigger_scraping'),
] 
