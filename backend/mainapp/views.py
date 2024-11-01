from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import SignupForm, CampaignForm  # Ensure both forms are imported
from .models import Campaign
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required
import re  # Import re directly
import stripe
from django.conf import settings
from django.views import View
from django.http import JsonResponse


User = get_user_model()  # Use the correct User model

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
stripe.api_key = 'sk_test_51QGGkRKGl5yjZXkwZ7L2CSJJvQDCK8WVLIhlDKMghNnCIuQttWAlBIg9uL7P80lciWWtBg3VIg94jydqu8ofPgf500oVp1ywqQ'

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
                messages.error(request, "Invalid email or password.")
                return render(request, 'login.html')
        else:
            username = username_or_email

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username/email or password.")
    
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

def campaign_success(request):
    return render(request, 'campaign_success.html')

@login_required
def profile_view(request):
    user = request.user
    campaigns = Campaign.objects.filter(user=user)
    contributions = user.payments.all()  # Corrected way to access user's payments
    
    return render(request, 'profile.html', {
        'user': user,
        'campaigns': campaigns,
        'contributions': contributions
    })

def campaign_view(request):
    campaigns = Campaign.objects.filter(approved=True)  # Display only approved campaigns
    return render(request, 'campaign_list.html', {'campaigns': campaigns})

@login_required
def edit_profile(request):
    # Placeholder for actual edit profile logic (implement form processing as needed)
    return render(request, 'edit_profile.html')

def campaign_detail(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    return render(request, 'detailcampaign.html', {'campaign': campaign})

class PaymentView(View):
    def post(self, request, campaign_id):
        campaign = get_object_or_404(Campaign, id=campaign_id)
        amount = request.POST.get('amount')

        # Create a Stripe Checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'inr',
                    'product_data': {
                        'name': campaign.title,
                    },
                    'unit_amount': int(amount) * 100,  # Amount in paise (e.g., 1000 for ₹10)
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://127.0.0.1:8000/success/',  # Change to your success URL
            cancel_url='http://127.0.0.1:8000/cancel/',  # Change to your cancel URL
        )
        return redirect(session.url, code=303)
def calculate_amount(campaign_id):
    # Your logic to calculate the payment amount based on the campaign
    # For example, return the campaign's goal amount
    return 5000  # Example amount in paise

class PaymentSuccessView(View):
    def get(self, request):
        # Get the payment intent from the URL parameter
        payment_intent = request.GET.get('payment_intent')

        # Verify the payment intent
        intent = stripe.PaymentIntent.retrieve(payment_intent)
        if intent.status == 'succeeded':
            # Get the user and campaign from the payment intent
            user_id = intent.metadata.get('user_id')
            campaign_id = intent.metadata.get('campaign_id')
            user = User.objects.get(id=user_id)
            campaign = Campaign.objects.get(id=campaign_id)

            # Create a new payment object for the user
            payment = user.payments.create(
                amount=intent.amount / 100,  # Convert amount from paise to rupees
                campaign=campaign
            )

            # Update the campaign's total contributions
            campaign.total_contributions += payment.amount
            campaign.save()

            # Redirect to the campaign success page
            return redirect('campaign_success')
        else:
            # Handle other payment intent statuses as needed
            pass
        # Redirect to the campaign detail page with an error message
        return redirect('campaign_detail', campaign_id=campaign_id)
    


class SuccessView(View):
    def get(self, request):
        return render(request, 'success.html')

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
            messages.success(request, 'Campaign created successfully!')
            return redirect('campaign_list')  # Redirect to the updated URL pattern
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CampaignForm()
    
    return render(request, 'createcampaign.html', {'form': form})

def create_campaign_view(request):
    if request.user.is_authenticated:
        return create_campaign(request)
    else:
        messages.error(request, 'You must be logged in to start a campaign.')
        return redirect('login')  # Adjust 'login' to your actual login URL name

@login_required
def edit_campaign(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id, user=request.user)
    if request.method == 'POST':
        form = CampaignForm(request.POST, request.FILES, instance=campaign)
        if form.is_valid():
            form.save()
            messages.success(request, 'Campaign updated successfully.')
            return redirect('campaign_detail', campaign_id=campaign.id)
    else:
        form = CampaignForm(instance=campaign)
    return render(request, 'edit_campaign.html', {'form': form})

@login_required
def approve_campaign(request, campaign_id):
    if request.user.is_superuser:
        campaign = get_object_or_404(Campaign, id=campaign_id)
        campaign.approved = True
        campaign.save()
        messages.success(request, 'Campaign approved successfully.')
    else:
        messages.error(request, 'You do not have permission to approve campaigns.')
    return redirect('admin_campaigns')

@login_required
def admin_campaigns(request):
    if request.user.is_superuser:
        campaigns = Campaign.objects.filter(approved=False)
        return render(request, 'admin_campaigns.html', {'campaigns': campaigns})
    else:
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('home')

@login_required
def reject_campaign(request, campaign_id):
    if request.user.is_superuser:
        campaign = get_object_or_404(Campaign, id=campaign_id)
        campaign.delete()
        messages.success(request, 'Campaign rejected and deleted successfully.')
    else:
        messages.error(request, 'You do not have permission to reject campaigns.')
    return redirect('admin_campaigns')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')
