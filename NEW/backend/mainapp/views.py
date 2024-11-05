from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from .forms import SignupForm, CampaignForm
from .models import Campaign, Payment
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
import re
import stripe
from django.conf import settings
from django.views import View
from django.http import HttpResponse, HttpResponseBadRequest
from django.template.loader import render_to_string
from xhtml2pdf import pisa
import random
import string
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.utils import timezone

User = get_user_model()  # Use the correct User model
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

def home_view(request):
    return render(request, 'base.html')

def login_view(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email')
        password = request.POST.get('password')
        if re.match(r"[^@]+@[^@]+\.[^@]+", username_or_email):
            try:
                username = User.objects.get(email=username_or_email).username
            except User.DoesNotExist:
                return render(request, 'login.html')  # Simplified error handling
        else:
            username = username_or_email
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
    return render(request, 'login.html')

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})

@login_required
def profile_view(request):
    user = request.user
    campaigns = Campaign.objects.filter(user=user)
    contributions = user.payments.all()  # Corrected related name if needed
    return render(request, 'profile.html', {
        'user': user,
        'campaigns': campaigns,
        'contributions': contributions
    })

def campaign_view(request):
    campaigns = Campaign.objects.filter(approved=True)  # Only get approved campaigns
    return render(request, 'campaign_list.html', {'campaigns': campaigns})

@login_required
def edit_profile(request):
    return render(request, 'edit_profile.html')  # Placeholder for actual logic
@login_required
def campaign_detail(request, campaign_id):
    # Get the campaign or return a 404 if not found
    campaign = get_object_or_404(Campaign, id=campaign_id)
    
    # Retrieve payments associated with the campaign
    payments = Payment.objects.filter(campaign=campaign)
    
    # Prepare the context with campaign details and payments
    context = {
        'campaign': campaign,
        'payments': payments,
    }
    
    # Render the detailcampaign.html template with the context
    return render(request, 'detailcampaign.html', context)
        
class CancelView(View):
    def get(self, request):
        return render(request, 'cancel.html')

@login_required
def create_campaign(request):
    if request.method == 'POST':
        form = CampaignForm(request.POST, request.FILES)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.user = request.user
            campaign.save()
            return redirect('campaign_list')
    else:
        form = CampaignForm()
    return render(request, 'createcampaign.html', {'form': form})


@login_required
def approve_campaign(request, campaign_id):
    if request.user.is_superuser:
        campaign = get_object_or_404(Campaign, id=campaign_id)
        campaign.approved = True
        campaign.save()
        return redirect('admin_campaigns')
    return redirect('home')

@login_required
def admin_campaigns(request):
    if request.user.is_superuser:
        campaigns = Campaign.objects.filter(approved=False)
        return render(request, 'admin_campaigns.html', {'campaigns': campaigns})
    return redirect('home')

@login_required
def reject_campaign(request, campaign_id):
    if request.user.is_superuser:
        campaign = get_object_or_404(Campaign, id=campaign_id)
        campaign.delete()
        return redirect('admin_campaigns')
    return redirect('home')

@login_required
def donate_view(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)

    if request.method == 'POST':
        # Get donation details from the form
        amount = float(request.POST.get('amount'))
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        currency = request.POST.get('currency', 'INR')

        # Create a Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': currency.lower(),
                    'product_data': {
                        'name': campaign.title,
                    },
                    'unit_amount': int(amount * 100),  # amount in cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'http://127.0.0.1:8000/receipt/{campaign_id}/?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url='http://127.0.0.1:8000/cancel/',
        )

        # Redirect to Stripe checkout
        return redirect(session.url, code=303)

    return render(request, 'donate.html', {'campaign': campaign})

class ReceiptView(View):
    def get(self, request, campaign_id):
        payment = get_object_or_404(Payment, campaign_id=campaign_id)
        campaign = payment.campaign

        session_id = request.GET.get('session_id', None)  # Get the session_id from query parameters


        context = {
            'username': payment.name,
            'amount': payment.amount,
            'transaction_time': payment.transaction_time,
            'campaign_name': campaign.title,
            'campaign_logo': campaign.logo.url if campaign.logo else None,
            'user_email': payment.email,
            'campaign_id': campaign_id,
            'session_id': session_id,
        }
        return render(request, 'receipt.html', context)


class PaymentSuccessView(View):
    @method_decorator(login_required)
    def get(self, request):
        # Your existing code to process the payment goes here.
        # For example, after validating the payment:

        # Assuming you have campaign_id and payment_id variables set:
        campaign_id = ...  # Get this from your payment data
        payment_id = ...   # Get this from your payment data

        # After successful payment, redirect to the receipt view
        return redirect(reverse('receipt', kwargs={'campaign_id': campaign_id, 'payment_id': payment_id}))
    

def payment_success(request):
    # Your existing payment processing logic here

    campaign_id = ...  # Get this from your payment data
    payment_id = ...   # Get this from your payment data

    # Redirect to the receipt view
    return redirect(reverse('receipt', kwargs={'campaign_id': campaign_id, 'payment_id': payment_id}))