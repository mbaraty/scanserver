from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('hidden/', views.hidden, name="hidden"),
    path('<int:pk>', views.file, name="file"),
    path('download_pdf/<int:pk>/', views.download_pdf, name='download_pdf'),
    path('download_jpg/<int:pk>/', views.download_jpg, name='download_jpg'),
]
