from django.urls import path
from . import views

urlpatterns=[
    
    path('home/', views.home , name='home'),
    path('register/', views.register , name='register'),
    path('Login/', views.Login , name='Login'),
    path('welcome/', views.welcome , name='welcome'),
    path('wallet/', views.wallet , name='wallet'),
    path('spending/', views.spending , name='spending'),
    #path('delete_spending/<int:spending_id>/', views.delete_spending, name='delete_spending'),
    path('add_money/', views.add_money , name='add_money'),
    
    path('LogOut/', views.LogOut , name='LogOut')
]
