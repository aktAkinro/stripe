from django.contrib import admin
from django.urls import path, include
from django_registration.backends.one_step.views import RegistrationView
from register.forms import UserForm


"""And I updated urls.py with the registration url. In addition to the registration url
 we’re including the one step registration urls from djano-registration and the auth urls from Django."""

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',
         RegistrationView.as_view(
             form_class=UserForm,
             success_url='/'
         ),
         name='django_registration_register',
    ),
    path('', include('django_registration.backends.one_step.urls')),
    path('', include('django.contrib.auth.urls')),
]