from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate, login,logout,user_logged_in
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import IntegrityError

# Create your views here.

def home(request):
    return render(request,'home.html')


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password != password_confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, 'register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request,'register.html')

        try:
            User.objects.create_user(username=username, email=email, password=password,is_active=False)
            messages.success(request, "Registration successful! Please login.")
            return redirect('login')
            
        except IntegrityError:
            messages.error(request, "That username is already taken.")
        except Exception as e:
            messages.error(request, "An error occurred. Please try again.")  
    return render(request, 'register.html')



def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username,password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request,"Waiting to approve by Admin")
        else:
            messages.error(request, "Incorrect username or password!")
    return render(request,'login.html')


def user_logout(request):
    logout(request)
    return redirect('login')



def adminDashboard(request):
    if request.user.is_superuser:
        users = User.objects.filter(is_active = False)
        total_customers = User.objects.count()
        if 'approve' in request.POST:
            id = request.POST.get('id')
            user = get_object_or_404(User,id = id)
            user.is_active = True
            user.save()
            messages.success(request, f"User {user.username} approved!")
            return redirect('admin-dashboard')
        
        elif 'reject' in request.POST:
            id = request.POST.get('id')
            user = get_object_or_404(User,id = id)
            user.delete()
            messages.success(request, f"User {user.username} rejected and removed.")
            return redirect('admin-dashboard')
    else:
        return redirect('login')
    return render(request,'adminDashboard.html',{'pending_requests':users,'total_customers':total_customers})

