from django import forms
from django.core.exceptions import ValidationError
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['display_photo', 'gender', 'contact_number']

    def clean_contact_number(self):
        contact_number = self.cleaned_data.get('contact_number')
        if not contact_number:
            raise forms.ValidationError("This field is required.")

        # Check if it starts with '09' and has exactly 11 digits
        if not contact_number.startswith('09') or len(contact_number) != 11 or not contact_number.isdigit():
            raise forms.ValidationError("Enter a valid contact number (11 digits starting with '09').")

        return contact_number
