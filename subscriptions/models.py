from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings

User = get_user_model()


"""
In order to handle customers and subscriptions correctly we'll need to store some information in our database. 
I created a new model called StripeCustomer which will store Stripe's customerId and subscriptionId and relate it back the Django auth user.
 This will allow us to fetch our customer and subscription data from Stripe.
 """
class StripeCustomer(models.Model):
    user = models.OneToOneField(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripeCustomerId = models.CharField(max_length=255)
    stripeSubscriptionId = models.CharField(max_length=255)

    def __str__(self):
        return self.user.email



"""with this We fetch the customerId and subscriptionId from Stripe every time we need them"""
