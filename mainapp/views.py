from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from .forms import SignupForm, CampaignForm  # Ensure both forms are imported
from .models import Campaign
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
import re  # Import re directly
import stripe
from django.conf import settings
from django.views import View
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa


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
                return render(request, 'login.html')  # Removed error message
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
    return render(request, 'edit_profile.html')  # Placeholder for actual edit profile logic


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


class PaymentSuccessView(View):
    def get(self, request):
        payment_intent = request.GET.get('payment_intent')
        intent = stripe.PaymentIntent.retrieve(payment_intent)
        
        if intent.status == 'succeeded':
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
        
        return redirect('campaign_detail', campaign_id=campaign_id)  # Handle other payment statuses


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
            return redirect('campaign_list')  # Redirect to the updated URL pattern
    else:
        form = CampaignForm()
    
    return render(request, 'createcampaign.html', {'form': form})


def create_campaign_view(request):
    if request.user.is_authenticated:
        return create_campaign(request)
    return redirect('login')  # Adjust 'login' to your actual login URL name


@login_required
def edit_campaign(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id, user=request.user)
    if request.method == 'POST':
        form = CampaignForm(request.POST, request.FILES, instance=campaign)
        if form.is_valid():
            form.save()
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


def logout_view(request):
    logout(request)
    return redirect('home')


def receipt(request):
    return render(request, 'receipt.html')


def download_receipt_pdf(request):
    # Fetch campaign details based on context (to be implemented)
    campaign = ...  
    context = {
        'campaign': campaign,
        'amount': ...,
        'date': ...,
        'transaction_id': ...,
        'user_name': ...,
        'user_email': ...
    }
    html = render_to_string('receipt.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="receipt.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('PDF generation failed')
    return response


def process_payment(request):
    return redirect('payment_success')  # Simplified for demo


class SuccessView(View):
    def get(self, request):
        transaction_id = request.GET.get('transaction_id')
        campaign_id = request.GET.get('campaign_id')
        amount = request.GET.get('amount')

        intent = stripe.PaymentIntent.retrieve(transaction_id)
        if intent.status == 'succeeded':
            user = request.user  # Assuming the user is logged in and accessible via request
            campaign = Campaign.objects.get(id=campaign_id)

            # Create a new payment object for the user
            payment = user.payments.create(
                amount=intent.amount / 100,  # Convert amount from paise to rupees
                campaign=campaign
            )

            # Update the campaign's total contributions
            campaign.total_contributions += payment.amount
            campaign.save()

            # Redirect to the success view
            return redirect('success', campaign_id=campaign_id, amount=amount, transaction_id=transaction_id)
        
        return redirect('campaign_detail', campaign_id=campaign_id)
