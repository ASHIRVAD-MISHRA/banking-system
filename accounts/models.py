"""
Banking System Models - OOP Implementation (FINAL VERSION)
Demonstrates: Inheritance, Encapsulation, Polymorphism, Abstraction

✅ FIXED: Related name conflicts resolved
✅ Each account type has unique related_name
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
import random
import string


# ============================================================================
# BASE CLASS - Demonstrates ABSTRACTION and ENCAPSULATION
# ============================================================================

class Account(models.Model):
    """
    Abstract Base Class for all bank accounts.
    Demonstrates: Abstraction, Encapsulation
    
    NOTE: customer field is defined in child classes to avoid related_name conflicts
    """
    
    # Account Types (used by child classes)
    SAVINGS = 'SAVINGS'
    CURRENT = 'CURRENT'
    
    ACCOUNT_TYPE_CHOICES = [
        (SAVINGS, 'Savings Account'),
        (CURRENT, 'Current Account'),
    ]
    
    # Encapsulated attributes
    account_number = models.CharField(max_length=12, unique=True, editable=False)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE_CHOICES)
    balance = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True  # Makes this an abstract base class
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.account_type} - {self.account_number}"
    
    # ========== ENCAPSULATION: Getter and Setter Methods ==========
    
    def get_balance(self):
        """Getter method for balance"""
        return self.balance
    
    def set_balance(self, amount):
        """Setter method with validation"""
        if amount < 0:
            raise ValueError("Balance cannot be negative")
        self.balance = amount
        self.save()
    
    # ========== ABSTRACTION: Interface Methods ==========
    
    def deposit(self, amount):
        """
        Deposit money into account.
        This method will be overridden in child classes (Polymorphism)
        """
        raise NotImplementedError("Subclass must implement deposit method")
    
    def withdraw(self, amount):
        """
        Withdraw money from account.
        This method will be overridden in child classes (Polymorphism)
        """
        raise NotImplementedError("Subclass must implement withdraw method")
    
    def get_minimum_balance(self):
        """
        Get minimum balance requirement.
        This method will be overridden in child classes (Polymorphism)
        """
        raise NotImplementedError("Subclass must implement get_minimum_balance method")
    
    # ========== HELPER METHODS ==========
    
    @staticmethod
    def generate_account_number():
        """Generate unique 12-digit account number"""
        return ''.join(random.choices(string.digits, k=12))
    
    def save(self, *args, **kwargs):
        """Override save to auto-generate account number"""
        if not self.account_number:
            self.account_number = self.generate_account_number()
        super().save(*args, **kwargs)


# ============================================================================
# CHILD CLASSES - Demonstrates INHERITANCE and POLYMORPHISM
# ============================================================================

class SavingsAccount(Account):
    """
    Savings Account - Inherits from Account base class.
    Demonstrates: Inheritance, Polymorphism
    
    ✅ FIXED: Uses unique related_name='savings_accounts'
    """
    
    # Customer field with UNIQUE related_name
    customer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='savings_accounts'  # ✅ Unique related name
    )
    
    # Class-level constants (encapsulation)
    MINIMUM_BALANCE = Decimal('500.00')
    INTEREST_RATE = Decimal('0.04')  # 4% annual interest
    WITHDRAWAL_LIMIT = Decimal('50000.00')  # Daily limit
    
    class Meta:
        verbose_name = 'Savings Account'
        verbose_name_plural = 'Savings Accounts'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.account_type = Account.SAVINGS
    
    # ========== POLYMORPHISM: Override parent methods ==========
    
    def deposit(self, amount):
        """
        Deposit money - Savings specific implementation.
        Overrides parent method (Polymorphism)
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        
        self.balance += Decimal(str(amount))
        self.save()
        
        # Create transaction record
        Transaction.objects.create(
            savings_account=self,
            transaction_type=Transaction.DEPOSIT,
            amount=amount,
            balance_after=self.balance,
            description=f"Deposit to {self.account_number}"
        )
        
        return True
    
    def withdraw(self, amount):
        """
        Withdraw money with savings account rules.
        Overrides parent method (Polymorphism)
        """
        amount = Decimal(str(amount))
        
        # Validation
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        
        if amount > self.WITHDRAWAL_LIMIT:
            raise ValueError(f"Daily withdrawal limit is {self.WITHDRAWAL_LIMIT}")
        
        if self.balance - amount < self.MINIMUM_BALANCE:
            raise ValueError(f"Insufficient balance. Minimum balance required: {self.MINIMUM_BALANCE}")
        
        # Perform withdrawal
        self.balance -= amount
        self.save()
        
        # Create transaction record
        Transaction.objects.create(
            savings_account=self,
            transaction_type=Transaction.WITHDRAWAL,
            amount=amount,
            balance_after=self.balance,
            description=f"Withdrawal from {self.account_number}"
        )
        
        return True
    
    def get_minimum_balance(self):
        """Return minimum balance for savings account"""
        return self.MINIMUM_BALANCE
    
    def calculate_interest(self):
        """Calculate and add interest (savings-specific feature)"""
        interest = self.balance * self.INTEREST_RATE / 12  # Monthly interest
        self.deposit(interest)
        return interest


class CurrentAccount(Account):
    """
    Current Account - Inherits from Account base class.
    Demonstrates: Inheritance, Polymorphism
    
    ✅ FIXED: Uses unique related_name='current_accounts'
    """
    
    # Customer field with UNIQUE related_name
    customer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='current_accounts'  # ✅ Unique related name
    )
    
    # Class-level constants (different from SavingsAccount)
    MINIMUM_BALANCE = Decimal('1000.00')
    OVERDRAFT_LIMIT = Decimal('10000.00')  # Can go negative
    TRANSACTION_FEE = Decimal('10.00')
    
    class Meta:
        verbose_name = 'Current Account'
        verbose_name_plural = 'Current Accounts'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.account_type = Account.CURRENT
    
    # ========== POLYMORPHISM: Different implementation than SavingsAccount ==========
    
    def deposit(self, amount):
        """
        Deposit money - Current account specific implementation.
        Different from SavingsAccount (Polymorphism)
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        
        self.balance += Decimal(str(amount))
        self.save()
        
        Transaction.objects.create(
            current_account=self,
            transaction_type=Transaction.DEPOSIT,
            amount=amount,
            balance_after=self.balance,
            description=f"Deposit to {self.account_number}"
        )
        
        return True
    
    def withdraw(self, amount):
        """
        Withdraw money with current account rules (allows overdraft).
        Different from SavingsAccount (Polymorphism)
        """
        amount = Decimal(str(amount))
        
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        
        # Current account allows overdraft
        if self.balance - amount < -self.OVERDRAFT_LIMIT:
            raise ValueError(f"Overdraft limit exceeded. Limit: {self.OVERDRAFT_LIMIT}")
        
        # Deduct transaction fee
        total_deduction = amount + self.TRANSACTION_FEE
        self.balance -= total_deduction
        self.save()
        
        # Create withdrawal transaction
        Transaction.objects.create(
            current_account=self,
            transaction_type=Transaction.WITHDRAWAL,
            amount=amount,
            balance_after=self.balance,
            description=f"Withdrawal from {self.account_number}"
        )
        
        # Create fee transaction
        Transaction.objects.create(
            current_account=self,
            transaction_type=Transaction.FEE,
            amount=self.TRANSACTION_FEE,
            balance_after=self.balance,
            description="Transaction fee"
        )
        
        return True
    
    def get_minimum_balance(self):
        """Return minimum balance for current account"""
        return self.MINIMUM_BALANCE


# ============================================================================
# TRANSACTION CLASS - Encapsulates transaction details
# ============================================================================

class Transaction(models.Model):
    """
    Transaction Model - Records all account transactions.
    Demonstrates: Encapsulation
    
    ✅ UPDATED: Separate ForeignKey fields for each account type
    """
    
    DEPOSIT = 'DEPOSIT'
    WITHDRAWAL = 'WITHDRAWAL'
    TRANSFER_IN = 'TRANSFER_IN'
    TRANSFER_OUT = 'TRANSFER_OUT'
    FEE = 'FEE'
    
    TRANSACTION_TYPES = [
        (DEPOSIT, 'Deposit'),
        (WITHDRAWAL, 'Withdrawal'),
        (TRANSFER_IN, 'Transfer In'),
        (TRANSFER_OUT, 'Transfer Out'),
        (FEE, 'Fee'),
    ]
    
    # Encapsulated attributes
    transaction_id = models.CharField(max_length=20, unique=True, editable=False)
    
    # Separate ForeignKey fields for each account type
    savings_account = models.ForeignKey(
        'SavingsAccount', 
        on_delete=models.CASCADE, 
        related_name='transactions', 
        null=True, 
        blank=True
    )
    current_account = models.ForeignKey(
        'CurrentAccount', 
        on_delete=models.CASCADE, 
        related_name='transactions', 
        null=True, 
        blank=True
    )
    
    transaction_type = models.CharField(max_length=15, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
    
    def __str__(self):
        return f"{self.transaction_type} - {self.amount} - {self.timestamp}"
    
    @property
    def account(self):
        """Helper property to get the associated account"""
        return self.savings_account or self.current_account
    
    @staticmethod
    def generate_transaction_id():
        """Generate unique transaction ID"""
        prefix = 'TXN'
        number = ''.join(random.choices(string.digits, k=10))
        return f"{prefix}{number}"
    
    def save(self, *args, **kwargs):
        """Override save to auto-generate transaction ID"""
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()
        super().save(*args, **kwargs)


# ============================================================================
# CUSTOMER PROFILE - Additional customer information
# ============================================================================

class CustomerProfile(models.Model):
    """
    Customer Profile - Extends Django User model.
    Demonstrates: Encapsulation, One-to-One relationship
    """
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15)
    address = models.TextField()
    date_of_birth = models.DateField()
    identity_proof = models.CharField(max_length=50)  # Aadhaar/PAN/Passport
    identity_number = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Customer Profile'
        verbose_name_plural = 'Customer Profiles'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.phone}"
    
    def get_total_balance(self):
        """Calculate total balance across all accounts"""
        # Use the correct related_names
        savings = self.user.savings_accounts.filter(is_active=True)
        current = self.user.current_accounts.filter(is_active=True)
        
        total = sum(acc.balance for acc in savings) + sum(acc.balance for acc in current)
        return total