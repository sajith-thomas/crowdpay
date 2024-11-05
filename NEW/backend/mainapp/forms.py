from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Campaign

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, min_length=6)
    confirm_password = forms.CharField(widget=forms.PasswordInput, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']  # Exclude confirm_password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)  # Create user instance without saving
        user.set_password(self.cleaned_data["password"])  # Hash the password
        if commit:
            user.save()  # Save the user instance
        return user


class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ['title', 'description', 'goal', 'image']
    
    def clean_goal(self):
        goal = self.cleaned_data.get("goal")
        if goal <= 0:
            raise ValidationError("Goal amount must be greater than zero.")
        return goal
    

class DonationForm(forms.Form):
    amount = forms.IntegerField(min_value=1, label='Amount (₹)', required=True)