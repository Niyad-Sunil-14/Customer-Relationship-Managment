from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import IntegrityError
from . forms import CustomerForm
from . models import Customer
# Create your views here.

def home(request):
    total_customers = Customer.objects.count()
    unassigned_customers = Customer.objects.filter(assigned_user__isnull=True).count()
    total_staff = User.objects.filter(is_active=True).count()
    pending_approvals = User.objects.filter(is_active=False).count()
    total_lead_converted = Customer.objects.filter(lead_status='converted').count()

    context = {
        'total_customers':total_customers,
        'total_staff':total_staff,
        'unassigned_customers':unassigned_customers,
        'pending_approvals':pending_approvals,
        'total_lead_converted':total_lead_converted,
    }
    return render(request,'home.html',context=context)


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



def requests(request):
    if request.user.is_superuser:
        users = User.objects.filter(is_active = False)
        if 'approve' in request.POST:
            id = request.POST.get('id')
            user = get_object_or_404(User,id = id)
            user.is_active = True
            user.save()
            messages.success(request, f"User {user.username} approved!")
            return redirect('requests')
        
        elif 'reject' in request.POST:
            id = request.POST.get('id')
            user = get_object_or_404(User,id = id)
            user.delete()
            messages.success(request, f"User {user.username} rejected and removed.")
            return redirect('requests')
    else:
        return redirect('login')
    return render(request,'requests.html',{'pending_requests':users})



def create_customer(request):
    form = CustomerForm()
    if not request.user.is_active:
        return redirect('login')

    if not request.user.is_superuser:
        if 'assigned_user' in form.fields:
            del form.fields['assigned_user']

    if request.method == 'POST':
        form = CustomerForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request,"Customer created successfully!")
            return redirect('create-customer')
        else:
            if not request.user.is_superuser:
                if 'assigned_user' in form.fields:
                    del form.fields['assigned_user']
         
    return render(request,'create_customer.html',{'form':form})



def customer_list(request):
    if not request.user.is_active:
        return redirect('login')

    if request.user.is_superuser:
        customer_list = Customer.objects.all()
    else:
        customer_list = Customer.objects.filter(assigned_user=request.user.id)
    return render(request,'customer_list.html',{'customer_list':customer_list})



def edit_customer(request,id):
    data = get_object_or_404(Customer,id=id)
    form = CustomerForm(instance=data)

    if not request.user.is_active:
        return redirect('login')
    
    if not request.user.is_superuser:
        if 'assigned_user' in form.fields:
            del form.fields['assigned_user']

    if request.method == 'POST':
        form = CustomerForm(request.POST,instance=data)
        if form.is_valid():
            customer = form.save(commit=False)
            if not request.user.is_superuser:
                customer.assigned_user = request.user
            customer.save()
            messages.success(request,"Customer updated successfully!")
            return redirect('edit-customer',id)
        else:
            if not request.user.is_superuser:
                if 'assigned_user' in form.fields:
                    del form.fields['assigned_user']

    return render(request,'edit_customer.html',{'form':form})