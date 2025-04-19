from django.urls import path
from . import views

app_name = 'themes'

urlpatterns = [
    path('templates/', views.template_dashboard, name='dashboard'),
    path('templates/preview/<int:template_id>/', views.preview_template, name='preview'),
    path('templates/create/', views.create_template, name='create_template'),
    path('templates/edit/<int:template_id>/', views.edit_template, name='edit_template'),
    path('templates/delete/<int:template_id>/', views.delete_template, name='delete_template'),
    path('templates/import/', views.import_template, name='import_template'),
    path('templates/export/<int:template_id>/', views.export_template, name='export_template'),
]