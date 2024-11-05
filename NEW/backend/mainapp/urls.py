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
    CancelView,
    campaign_detail,
    donate_view,
    ReceiptView,
    PaymentSuccessView,

    
    

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
    path('cancel/', CancelView.as_view(), name='cancel'),
    path('donate/<int:campaign_id>/', donate_view, name='donate'),
    path('receipt/<int:campaign_id>/', ReceiptView.as_view(), name='receipt'),
    path('payment-success/', PaymentSuccessView.as_view(), name='payment_success'),


]

