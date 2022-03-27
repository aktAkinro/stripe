from unicodedata import name
from django.urls import path
from . import views

urlpatterns = [
    path('home', views.home, name='subscriptions-home'), #Assigned a URL to the home view
    path('dashboard', views.dashboard, name='subscriptions-dashboard'), #Assigned a URL to the dashboard view 
    path('config/', views.stripe_config),
    path('create-checkout-session/', views.create_checkout_session),
    path('webhook/', views.stripe_webhook),
    path('success/', views.success),  
    path('cancel/', views.cancel, name='subscriptions-cancel'), 
    
]