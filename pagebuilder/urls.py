# In pagebuilder/urls.py

from django.urls import path
from . import views

app_name = 'pagebuilder'

urlpatterns = [
    path('preview-template/<str:template_name>/', views.preview_template, name='preview_template'),
]