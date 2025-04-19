from django.urls import path
from . import views

urlpatterns = [
    # Home page
    path('', views.HomePageView.as_view(), name='home'),
    
    # Form submission handlers
    path('contact/submit/', views.ContactFormView.as_view(), name='contact_submit'),
    path('newsletter/subscribe/', views.NewsletterFormView.as_view(), name='newsletter_subscribe'),
    
    # Dynamic page detail (should be last)
    path('<slug:slug>/', views.PageDetailView.as_view(), name='page_detail'),
]