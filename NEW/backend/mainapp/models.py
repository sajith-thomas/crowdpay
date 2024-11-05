from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_pics', default='default.jpg')

    def __str__(self):
        return f'{self.user.username} Profile'


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

    def total_payments(self):
        """Calculate the total amount raised from payments."""
        return sum(payment.amount for payment in self.payment_set.all())


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments') 
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    amount = models.FloatField()
    currency = models.CharField(max_length=10, default='INR')  # Add a default value
    anonymous = models.BooleanField(default=False)
    transaction_time = models.DateTimeField(auto_now_add=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, null=True, blank=True)

    

    def __str__(self):
        return f'Payment {self.id} - {self.name if self.name else "Anonymous"}'

    def get_campaign_title(self):
        """Get the title of the associated campaign."""
        return self.campaign.title if self.campaign else 'No Campaign'

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
