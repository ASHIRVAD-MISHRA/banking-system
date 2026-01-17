"""
URL Configuration for Banking System
Maps URLs to view functions
"""

from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Account Management
    path('create-account/', views.create_account, name='create_account'),
    path('account/<str:account_number>/', views.account_detail, name='account_detail'),
    
    # Transactions
    path('deposit/<str:account_number>/', views.deposit_money, name='deposit_money'),
    path('withdraw/<str:account_number>/', views.withdraw_money, name='withdraw_money'),
    path('transfer/<str:account_number>/', views.transfer_money, name='transfer_money'),
    path('history/<str:account_number>/', views.transaction_history, name='transaction_history'),
]