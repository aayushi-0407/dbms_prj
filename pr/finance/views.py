from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.utils import timezone
from django.db import connection

# @login_required
# def delete_spending(request, spending_id):
#     with connection.cursor() as cursor:
#         # Retrieve spending details
#         cursor.execute("SELECT amount, user_id FROM Spending WHERE spending_id = %s", [spending_id])
#         row = cursor.fetchone()
#         amount, user_id = row[0], row[1]

#         # Delete the spending
#         cursor.execute("DELETE FROM Spending WHERE spending_id = %s", [spending_id])

#         # Update wallet balance
#         cursor.execute("UPDATE Wallet SET balance = balance + %s WHERE user_id = %s", [amount, user_id])

#     return redirect('wallet')

@login_required
def delete_spending(request, spending_id):
    with connection.cursor() as cursor:
        # Retrieve the spending instance
        cursor.execute("SELECT * FROM Spending WHERE spending_id = %s", [spending_id])
        spending = cursor.fetchone()

        # Ensure that the spending exists and belongs to the user
        if spending and spending[1] == request.user.id:
            # Get the wallet associated with the user
            cursor.execute("SELECT * FROM Wallet WHERE user_id = %s", [request.user.id])
            user_wallet = cursor.fetchone()

            # Update the wallet balance by adding back the spent amount
            new_balance = user_wallet[2] + spending[2]
            cursor.execute("UPDATE Wallet SET balance = %s WHERE user_id = %s", [new_balance, request.user.id])

            # Delete the spending instance
            cursor.execute("DELETE FROM Spending WHERE spending_id = %s", [spending_id])

    return redirect('wallet')

@login_required
def add_money(request):
    user = request.user

    with connection.cursor() as cursor:
        try:
            # Attempt to get the user's wallet
            cursor.execute("SELECT * FROM Wallet WHERE user_id = %s", [user.id])
            user_wallet = cursor.fetchone()

            if not user_wallet:
                # If the wallet doesn't exist, create a new one
                cursor.execute("INSERT INTO Wallet (user_id, balance) VALUES (%s, 0)", [user.id])
                user_wallet = cursor.fetchone()

            if request.method == 'POST':
                amount_str = request.POST.get('amount')

                try:
                    amount = Decimal(amount_str)
                except ValueError:
                    return HttpResponse("Invalid amount. Please enter a valid number.")

                if amount <= 0:
                    return HttpResponse("Invalid amount. Please enter a positive number.")

                # Update the user's wallet balance
                new_balance = user_wallet[2] + amount
                cursor.execute("UPDATE Wallet SET balance = %s WHERE user_id = %s", [new_balance, user.id])

                return redirect("wallet")

        except Exception as e:
            return HttpResponse("An error occurred while processing your request.")

    return render(request, 'add_money.html')

@login_required
def wallet(request):
    if not request.user.is_authenticated:
        return HttpResponse("No user found")

    with connection.cursor() as cursor:
        try:
            # Retrieve user's wallet and spendings
            cursor.execute("SELECT * FROM Wallet WHERE user_id = %s", [request.user.id])
            user_wallet = cursor.fetchone()

            cursor.execute("SELECT amount, description, date FROM Spending WHERE user_id = %s", [request.user.id])
            user_spendings = cursor.fetchall()
        except Exception as e:
            return HttpResponse("An error occurred while processing your request.")

    return render(request, 'wallet.html', {'user_wallet': user_wallet, 'user_spendings': user_spendings})


@login_required
def spending(request):
    if request.method == "POST":
        amount_str = request.POST.get('amount')
        desc = request.POST.get('description')
        user = request.user

        try:
            amount = Decimal(amount_str)
        except ValueError:
            return HttpResponse("Invalid amount. Please enter a valid number.")

        if amount <= 0:
            return HttpResponse("Invalid amount. Please enter a positive number.")

        with connection.cursor() as cursor:
            try:
                # Insert spending record
                cursor.execute("INSERT INTO Spending (user_id, amount, description, date) VALUES (%s, %s, %s, %s)", [user.id, amount, desc, timezone.now()])

                # Update user's wallet balance
                cursor.execute("UPDATE Wallet SET balance = balance - %s WHERE user_id = %s", [amount, user.id])

                return redirect("wallet")

            except Exception as e:
                return HttpResponse("An error occurred while processing your request.")

    return render(request, 'spending.html')

def register(request):
    error_message = ""
    if request.method == "POST":
        firstname = request.POST.get('first_name')
        lastname = request.POST.get('last_name')
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if the username already exists
        user_exists = User.objects.filter(username=username).exists()

        if user_exists:
            error_message = "Username already exists. Please choose a different username."
            return render(request, 'register.html', {'error_message': error_message})
        else:
            # If username does not exist, create a new user
            user = User.objects.create(first_name=firstname, last_name=lastname, username=username)
            user.set_password(password)
            user.save()
            return render(request, 'login.html')
    return render(request, 'register.html', {'error_message': error_message})

def Login(request):
    if request.method=="POST":
        username=request.POST.get('username')
        password=request.POST.get('password')
        if not User.objects.filter(username=username).exists():
            return render('login.html')

        user=authenticate(username=username,password=password)

        if user is None:
            return render(request,'login.html')
        else:
            login(request,user)
            return render(request,'welcome.html')

    return render(request,'Login.html')

def LogOut(request):
    logout(request)
    return render(request,'home.html')

def welcome(request):
    return render(request, 'welcome.html', {'username': request.user.username})

def home(request):
    return render(request, "home.html")
