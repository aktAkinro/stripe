from django_registration.forms import RegistrationForm
from .models import User

class UserForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = User