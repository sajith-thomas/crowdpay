from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login,  authenticate
from django.contrib.auth.models import User
from .forms import SignupForm, CampaignForm
from .models import Campaign, Payment, Profile
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
import re
import stripe, razorpay
from django.conf import settings
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.contrib import messages
import uuid


# Create your views here.

User = get_user_model()  # Use the correct User model

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY




def home_view(request):
    campaigns = Campaign.objects.all()  # Fetch all campaigns from the database
    return render(request, 'base.html', {'campaigns': campaigns})

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
    
    # Get user profile
    user_profile = Profile.objects.get(user=user)
    user_profile, created = Profile.objects.get_or_create(user=user)
    campaigns = Campaign.objects.filter(user=user)
    
    # Retrieve contributions (payments made by the user)
    contributions = Payment.objects.filter(user=user)
    
    return render(request, 'profile.html', {
        'user': user,
        'user_profile': user_profile,
        'campaigns': campaigns,
        'contributions': contributions,
        'payments': contributions,  # Alias if needed for template consistency
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


def search(request):
    query = request.GET.get('q', '')  # Get the search query from the GET request
    results = Campaign.objects.filter(title__icontains=query) | Campaign.objects.filter(description__icontains=query)  # Filter campaigns by title or description
    return render(request, 'search_results.html', {'query': query, 'results': results})  



@login_required
def donate_view(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'GET':
        amount = request.GET.get('amount', 0)
        return render(request, 'donate.html', {'campaign': campaign, 'amount': amount})

    elif request.method == 'POST':
        amount = int(request.POST['amount'])
        payment_method = request.POST.get('payment_method')

        # Redirect to appropriate payment handler
        if payment_method == 'stripe':
            return stripe_payment(request, campaign, amount)
        elif payment_method == 'razorpay':
            return razorpay_payment(request, campaign, amount)

        messages.error(request, "Invalid payment method.")
        return redirect('campaign_detail', campaign_id=campaign_id)

def stripe_payment(request, campaign, amount):
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'inr',
                'product_data': {
                    'name': campaign.title,
                },
                'unit_amount': amount * 100,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri(reverse('stripe_success', args=[campaign.id])),
        cancel_url=request.build_absolute_uri(reverse('stripe_cancel')),
    )

    # Save pending payment
    Payment.objects.create(
        user=request.user,
        campaign=campaign,
        amount=amount,
        payment_method="stripe",
        transaction_id=checkout_session.id,
        status="pending"
    )

    return redirect(checkout_session.url, code=303)

@login_required
def stripe_success(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    payment = Payment.objects.get(user=request.user, campaign=campaign, payment_method="stripe", status="pending")

    payment.status = "completed"
    payment.save()

    campaign.raised_amount += payment.amount
    campaign.save()

    profile = Profile.objects.get(user=request.user)
    profile.contributions += payment.amount
    profile.save()

    messages.success(request, "Payment successful! Your contribution has been recorded.")
    return redirect('campaign_list')

def razorpay_payment(request, campaign, amount):
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
    razorpay_order = client.order.create({
        'amount': amount * 100,  # Razorpay requires amount in paise
        'currency': 'INR',
        'payment_capture': '1'
    })

    # Save pending payment
    Payment.objects.create(
        user=request.user,
        campaign=campaign,
        amount=amount,
        payment_method="razorpay",
        transaction_id=razorpay_order['id'],
        status="pending"
    )

    context = {
        "campaign": campaign,
        "razorpay_order_id": razorpay_order['id'],
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "amount": amount,
    }
    return render(request, "razorpay_payment.html", context)

@csrf_exempt
def razorpay_callback(request):
    if request.method == "POST":
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')

        payment = get_object_or_404(Payment, transaction_id=order_id, payment_method="razorpay", status="pending")

        payment.status = "completed"
        payment.save()

        payment.campaign.raised_amount += payment.amount
        payment.campaign.save()

        profile = Profile.objects.get(user=payment.user)
        profile.contributions += payment.amount
        profile.save()

        messages.success(request, "Payment successful! Your contribution has been recorded.")
        return redirect('campaign_detail', campaign_id=payment.campaign.id)
    return redirect('home')


def generate_unique_transaction_id():
    transaction_id = str(uuid.uuid4())
    while Payment.objects.filter(transaction_id=transaction_id).exists():
        transaction_id = str(uuid.uuid4())
    return transaction_id

def stripe_cancel(request):
    messages.info(request, "Payment was cancelled.")
    return redirect('home')


def contact_view(request):
    return render(request, 'contact.html')

def about_view(request):
    return render(request, 'about.html')