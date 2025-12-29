from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    home_view,
    signup_view,
    campaign_view,
    create_campaign,
    profile_view,
    login_view,
    edit_profile,
    approve_campaign,
    admin_campaigns,
    reject_campaign,
    campaign_detail,
    search,
    stripe_payment,
    stripe_success,
    razorpay_payment,
    razorpay_callback,
    donate_view,
    stripe_cancel,
    contact_view,
    about_view,




)

urlpatterns = [
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('campaigns/', campaign_view, name='campaign_list'),
    path('createcampaign/', create_campaign, name='create_campaign'),
    path('profile/', profile_view, name='profile'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('edit_profile/', edit_profile, name='edit_profile'),
    path('campaign/<int:campaign_id>/', campaign_detail, name='campaign_detail'),
    path('admin/campaigns/', admin_campaigns, name='admin_campaigns'),
    path('approve_campaign/<int:campaign_id>/', approve_campaign, name='approve_campaign'),
    path('reject-campaign/<int:campaign_id>/', reject_campaign, name='reject_campaign'),
    path('search/', search, name='search'),
    path('campaign/<int:campaign_id>/stripe_payment/', stripe_payment, name='stripe_payment'),
    path('campaign/<int:campaign_id>/stripe_success/', stripe_success, name='stripe_success'),
    path('campaign/<int:campaign_id>/razorpay_payment/', razorpay_payment, name='razorpay_payment'),
    path('razorpay_callback/',razorpay_callback, name='razorpay_callback'),
    path('campaign/<int:campaign_id>/donate/',donate_view, name='donate'),
    path('stripe-cancel/', stripe_cancel, name='stripe_cancel'),
    path('contact/', contact_view, name='contact'),
    path('about/', about_view, name='about'),

   

]

