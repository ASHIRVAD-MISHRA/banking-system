"""
Admin Panel Configuration
Provides admin interface for managing accounts and transactions
"""

from django.contrib import admin
from .models import SavingsAccount, CurrentAccount, Transaction, CustomerProfile


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    """Admin interface for Customer Profiles"""
    
    list_display = ['user', 'phone', 'identity_proof', 'created_at']
    list_filter = ['identity_proof', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone', 'identity_number']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Contact Details', {
            'fields': ('phone', 'address')
        }),
        ('Identity Information', {
            'fields': ('date_of_birth', 'identity_proof', 'identity_number')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


@admin.register(SavingsAccount)
class SavingsAccountAdmin(admin.ModelAdmin):
    """Admin interface for Savings Accounts"""
    
    list_display = ['account_number', 'customer', 'balance', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['account_number', 'customer__username', 'customer__email']
    readonly_fields = ['account_number', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Account Information', {
            'fields': ('account_number', 'customer', 'account_type')
        }),
        ('Balance', {
            'fields': ('balance',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Make account_number readonly after creation"""
        if obj:  # Editing existing object
            return self.readonly_fields + ['customer', 'account_type']
        return self.readonly_fields


@admin.register(CurrentAccount)
class CurrentAccountAdmin(admin.ModelAdmin):
    """Admin interface for Current Accounts"""
    
    list_display = ['account_number', 'customer', 'balance', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['account_number', 'customer__username', 'customer__email']
    readonly_fields = ['account_number', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Account Information', {
            'fields': ('account_number', 'customer', 'account_type')
        }),
        ('Balance', {
            'fields': ('balance',),
            'description': 'Current accounts can have negative balance (overdraft)'
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Make account_number readonly after creation"""
        if obj:  # Editing existing object
            return self.readonly_fields + ['customer', 'account_type']
        return self.readonly_fields


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Admin interface for Transactions"""
    
    list_display = ['transaction_id', 'get_account', 'transaction_type', 'amount', 'balance_after', 'timestamp']
    list_filter = ['transaction_type', 'timestamp']
    search_fields = ['transaction_id', 'account__account_number', 'current_account__account_number']
    readonly_fields = ['transaction_id', 'timestamp']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Transaction Information', {
            'fields': ('transaction_id', 'account', 'current_account', 'transaction_type')
        }),
        ('Amount Details', {
            'fields': ('amount', 'balance_after')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Timestamp', {
            'fields': ('timestamp',)
        }),
    )
    
    def get_account(self, obj):
        """Display account number in list"""
        if obj.account:
            return obj.account.account_number
        elif obj.current_account:
            return obj.current_account.account_number
        return "N/A"
    
    get_account.short_description = 'Account Number'
    
    def has_add_permission(self, request):
        """Disable manual transaction creation from admin"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable transaction editing from admin"""
        return False


# Customize admin site headers
admin.site.site_header = "Banking System Administration"
admin.site.site_title = "Banking Admin"
admin.site.index_title = "Welcome to Banking System Admin Panel"