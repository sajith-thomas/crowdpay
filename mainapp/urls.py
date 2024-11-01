from django.urls import path
from django.contrib.auth import views as auth_views
from .views import PaymentView  # Change 'payment' to 'PaymentView'
from django.views.generic import TemplateView
from .views import (
    home_view,
    signup_view,
    campaign_view,
    create_campaign,
    profile_view,
    login_view,
    campaign_success,
    edit_profile,
    campaign_detail,
    approve_campaign,
    admin_campaigns,
    reject_campaign,
    PaymentView,
    SuccessView,
    CancelView,
    PaymentView,
    create_campaign_view,

)

urlpatterns = [
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('campaigns/', campaign_view, name='campaign_list'),
    path('createcampaign/',create_campaign, name='create_campaign'),
    path('profile/', profile_view, name='profile'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('campaign_success/', campaign_success, name='campaign_success'),
    path('edit_profile/', edit_profile, name='edit_profile'),
    path('campaign/<int:campaign_id>/', campaign_detail, name='campaign_detail'),
    path('campaign/<int:campaign_id>/payment/', PaymentView.as_view(), name='payment'),
    path('admin/campaigns/', admin_campaigns, name='admin_campaigns'),
    path('approve_campaign/<int:campaign_id>/', approve_campaign, name='approve_campaign'),
    path('reject-campaign/<int:campaign_id>/', reject_campaign, name='reject_campaign'),
    path('payment/success/', TemplateView.as_view(template_name='payment_success.html'), name='payment_success'),
    path('success/', SuccessView.as_view(), name='success'),
    path('cancel/', CancelView.as_view(), name='cancel'),
     path('create_campaign/', create_campaign_view, name='create_campaign'),
]
