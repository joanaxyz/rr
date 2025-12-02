from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from .models import User
from owner_verification.models import BusinessApplication

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
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Email address or Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )

    def clean(self):
        username_or_email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username_or_email and password:
            # Try to authenticate with username first
            user = authenticate(username=username_or_email, password=password)
            
            # If that fails, try with email
            if user is None:
                try:
                    user_obj = User.objects.get(email=username_or_email)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None
            
            if user is None:
                raise forms.ValidationError(
                    _("The email/username or password you entered is incorrect. Please try again."),
                    code='invalid_login'
                )
            else:
                self.confirm_login_allowed(user)
                self.user_cache = user
        return self.cleaned_data


class BusinessForm(forms.ModelForm):
    class Meta:
        model = BusinessApplication
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


class BusinessApplicationForm(forms.ModelForm):
    class Meta:
        model = BusinessApplication
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