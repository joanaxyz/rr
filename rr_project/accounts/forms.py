from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from .models import User
from owner_verification.models import OwnerVerificationRequest  # Correct model

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'})
    )
    username = forms.EmailField(
        max_length=100, 
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Email address'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'})
    )
    role = forms.CharField(
        widget=forms.TextInput()
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'password1', 'password2', 'role')

    def clean_username(self):
        email = self.cleaned_data['username']
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError(
                _("This email is already in use."),
                code='invalid_email'
            )
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = user.username
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Email address'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if user is None:
                raise forms.ValidationError(
                    _("The email or password you entered is incorrect. Please try again."),
                    code='invalid_login'
                )
            else:
                self.confirm_login_allowed(user)
                self.user_cache = user
        return self.cleaned_data


class OwnerForm(forms.ModelForm):
    class Meta:
        model = OwnerVerificationRequest  # Use the correct model
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make these fields optional
        for field_name in [
            'user', 'govt_full_name', 'government_id_type',
            'government_id_number', 'status'
        ]:
            if field_name in self.fields:
                self.fields[field_name].required = False


class OwnerVerificationForm(forms.ModelForm):
    class Meta:
        model = OwnerVerificationRequest
        fields = [
            "govt_full_name",
            "government_id_type",
            "government_id_number",
            "business_address",
            "business_email",
            "business_license",
            "government_id_front",
            "government_id_back",
            "proof_of_ownership",
            # 'state' is optional because it defaults to PENDING
        ]


class DeleteAccountForm(forms.Form):
    """Form for confirming account deletion"""
    confirm_delete = forms.BooleanField(
        required=True,
        label="I understand that deleting my account is permanent and cannot be undone",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    password = forms.CharField(
        required=True,
        label="Enter your password to confirm",
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password', 'class': 'form-control'})
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not self.user.check_password(password):
            raise forms.ValidationError(
                _("The password you entered is incorrect."),
                code='invalid_password'
            )
        return password