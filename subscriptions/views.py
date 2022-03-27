from pyexpat.errors import messages
import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User  # new
from django.http.response import JsonResponse, HttpResponse  # updated
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from subscriptions.models import StripeCustomer  # new
from django.contrib.auth import get_user_model


User = get_user_model()

#Created a new view called home, which will serve as our main index page.
#to associate Django users with Stripe customers and implement subscription management in the future,
#  we'll need to enforce user authentication before allowing customers to subscribe to the service. 
# We can achieve this by adding a @login_required decorator to all views that require authentication.
@login_required
def home(request):
    return render(request, 'home.html')


# new
@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)



""" if the request method is GET, we defined a domain_url, assigned the Stripe secret key to stripe.
api_key (so it will be sent automatically when we make a request to create a new Checkout Session), 
created the Checkout Session, and sent the ID back in the response."""

"""The user will be redirected back to those URLs in the event of a successful payment or cancellation, respectively"""


@csrf_exempt
def create_checkout_session(request):
    if request.method == 'GET':
        domain_url = 'http://localhost:8000/'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            checkout_session = stripe.checkout.Session.create(
                client_reference_id=request.user.id if request.user.is_authenticated else None,
                success_url=domain_url + 'success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url + 'cancel/',

                subscription_data={
                'trial_period_days': 7
            },

                payment_method_types=['card'],
                mode='subscription',
                line_items=[
                    {
                        'price': settings.STRIPE_PRICE_ID,
                        'quantity': 1,
                    }
                ]
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})



@login_required
def success(request):
    return render(request, 'success.html')


    

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')
    

@login_required
def cancel(request):
    customers = StripeCustomer.objects.all()
    stripe.api_key = settings.STRIPE_SECRET_KEY
    customer = StripeCustomer.objects.filter(user__pk=request.user.id).first()
    stripe.Subscription.delete(customer.stripeCustomerId)
    return render(request, 'cancel.html')



"""stripe_webhook which will create a new StripeCustomer every time someone subscribes to our service. 
stripe_webhook now serves as our webhook endpoint. Here, we're only looking for checkout.session.completed events 
which are called whenever a checkout is successful,"""

@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Fetch all the required data from session
        client_reference_id = session.get('client_reference_id')
        stripe_customer_id = session.get('customer')
        stripe_subscription_id = session.get('subscription')

        # Get the user and create a new StripeCustomer
        user = User.objects.get(id=client_reference_id)
        StripeCustomer.objects.create(
            user=user,
            stripeCustomerId=stripe_customer_id,
            stripeSubscriptionId=stripe_subscription_id,
        )
        print(user.email + ' just subscribed.')

    return HttpResponse(status=200)
