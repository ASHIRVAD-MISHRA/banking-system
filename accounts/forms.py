"""
Banking System Forms - Input Validation and User Interface
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import CustomerProfile, SavingsAccount, CurrentAccount
from datetime import date


class RegistrationForm(UserCreationForm):
    """
    User Registration Form with extended fields.
    Validates user input and creates account.
    """
    
    # Basic user fields
    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    
    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    
    # Customer profile fields
    phone = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number'
        })
    )
    
    address = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Full Address',
            'rows': 3
        })
    )
    
    date_of_birth = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    IDENTITY_CHOICES = [
        ('aadhaar', 'Aadhaar Card'),
        ('pan', 'PAN Card'),
        ('passport', 'Passport'),
        ('license', 'Driving License'),
    ]
    
    identity_proof = forms.ChoiceField(
        choices=IDENTITY_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    identity_number = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Identity Number'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Password'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Confirm Password'
            }),
        }
    
    def clean_email(self):
        """Validate email uniqueness"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email
    
    def clean_phone(self):
        """Validate phone number"""
        phone = self.cleaned_data.get('phone')
        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")
        if len(phone) < 10:
            raise forms.ValidationError("Phone number must be at least 10 digits.")
        return phone
    
    def clean_date_of_birth(self):
        """Validate age (must be 18+)"""
        dob = self.cleaned_data.get('date_of_birth')
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        
        if age < 18:
            raise forms.ValidationError("You must be at least 18 years old to register.")
        
        return dob
    
    def save(self, commit=True):
        """Save user and create customer profile"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            
            # Create customer profile
            CustomerProfile.objects.create(
                user=user,
                phone=self.cleaned_data['phone'],
                address=self.cleaned_data['address'],
                date_of_birth=self.cleaned_data['date_of_birth'],
                identity_proof=self.cleaned_data['identity_proof'],
                identity_number=self.cleaned_data['identity_number']
            )
        
        return user


class AccountCreationForm(forms.Form):
    """
    Form to create new bank account (Savings or Current).
    """
    
    ACCOUNT_CHOICES = [
        ('savings', 'Savings Account (Min Balance: ₹500, Interest: 4%)'),
        ('current', 'Current Account (Min Balance: ₹1000, Overdraft: ₹10000)'),
    ]
    
    account_type = forms.ChoiceField(
        choices=ACCOUNT_CHOICES,
        required=True,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        })
    )
    
    initial_deposit = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Initial Deposit Amount',
            'step': '0.01'
        })
    )
    
    def clean_initial_deposit(self):
        """Validate initial deposit based on account type"""
        deposit = self.cleaned_data.get('initial_deposit')
        account_type = self.data.get('account_type')
        
        if account_type == 'savings' and deposit < 500:
            raise forms.ValidationError("Minimum initial deposit for Savings Account is ₹500")
        
        if account_type == 'current' and deposit < 1000:
            raise forms.ValidationError("Minimum initial deposit for Current Account is ₹1000")
        
        return deposit


class DepositForm(forms.Form):
    """Form for depositing money"""
    
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=1,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter amount to deposit',
            'step': '0.01'
        })
    )
    
    def clean_amount(self):
        """Validate deposit amount"""
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be positive.")
        if amount > 1000000:
            raise forms.ValidationError("Single deposit cannot exceed ₹10,00,000")
        return amount


class WithdrawalForm(forms.Form):
    """Form for withdrawing money"""
    
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=1,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter amount to withdraw',
            'step': '0.01'
        })
    )
    
    def clean_amount(self):
        """Validate withdrawal amount"""
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be positive.")
        return amount


class TransferForm(forms.Form):
    """Form for transferring funds between accounts"""
    
    from_account = forms.CharField(
        max_length=12,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'From Account Number',
            'readonly': True
        })
    )
    
    to_account = forms.CharField(
        max_length=12,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'To Account Number'
        })
    )
    
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=1,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Amount to transfer',
            'step': '0.01'
        })
    )
    
    description = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Description (optional)'
        })
    )
    
    def clean_to_account(self):
        """Validate recipient account exists"""
        account_number = self.cleaned_data.get('to_account')
        
        # Check in both account types
        savings_exists = SavingsAccount.objects.filter(
            account_number=account_number,
            is_active=True
        ).exists()
        
        current_exists = CurrentAccount.objects.filter(
            account_number=account_number,
            is_active=True
        ).exists()
        
        if not (savings_exists or current_exists):
            raise forms.ValidationError("Invalid account number or account not active.")
        
        return account_number
    
    def clean(self):
        """Validate that from and to accounts are different"""
        cleaned_data = super().clean()
        from_acc = cleaned_data.get('from_account')
        to_acc = cleaned_data.get('to_account')
        
        if from_acc == to_acc:
            raise forms.ValidationError("Cannot transfer to the same account.")
        
        return cleaned_data


class SearchAccountForm(forms.Form):
    """Form to search for accounts"""
    
    search_query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by account number, username, or email'
        })
    )