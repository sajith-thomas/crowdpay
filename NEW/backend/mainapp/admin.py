from django.contrib import admin
from .models import Campaign

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'goal', 'raised_amount', 'created_at', 'approved')
    list_filter = ('approved',)
    search_fields = ('title', 'description')

    def approve_campaign(self, request, queryset):
        queryset.update(approved=True)
        self.message_user(request, f"{queryset.count()} campaigns approved.")

    def reject_campaign(self, request, queryset):
        queryset.update(approved=False)
        self.message_user(request, f"{queryset.count()} campaigns rejected.")

    actions = [approve_campaign, reject_campaign]
