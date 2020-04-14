from django.contrib import admin
from django.urls import path
from landing_page import views

urlpatterns = [
    # path('', views.AboutView.as_view(), name='about'),
    path('', views.register, name='about'),
    path('yoga_guide', views.VideoPageView.as_view(), name='all_video'),
    path('unsubscribe', views.UnsubscribeView.as_view(), name='unsubscribe')
]
