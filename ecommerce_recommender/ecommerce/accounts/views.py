from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import User, UserActivity
from products.models import Product, Purchase

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        is_staff = request.POST.get('is_staff', False) == 'on'
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_staff=is_staff
        )
        login(request, user)
        return redirect('user_dashboard')
    
    return render(request, 'accounts/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('admin_dashboard')
            return redirect('user_dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def user_dashboard(request):
    return redirect('product_list')

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    users = User.objects.all()
    return render(request, 'accounts/admin_dashboard.html', {'users': users})

@login_required
@user_passes_test(lambda u: u.is_staff)
def user_activity(request, user_id):
    user = User.objects.get(id=user_id)
    activities = UserActivity.objects.filter(user=user).order_by('-timestamp')
    return render(request, 'accounts/user_activity.html', {
        'selected_user': user,
        'activities': activities
    })