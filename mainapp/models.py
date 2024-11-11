from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Campaign(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    goal = models.DecimalField(max_digits=10, decimal_places=2, help_text="Enter amount in rupees")
    raised_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)  # Admin approval field

    def __str__(self):
        return self.title

    def owner_username(self):
        return self.user.username  # Return the owner's username

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contributions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_contributions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Other profile fields as needed
    
    def __str__(self):
        return f'{self.user.username} Profile'

class Payment(models.Model):
    PAYMENT_CHOICES = (("stripe", "Stripe"), ("razorpay", "Razorpay"))
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES,null=True, blank=True)
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, default="pending")