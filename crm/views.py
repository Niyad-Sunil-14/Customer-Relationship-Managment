from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import IntegrityError
from . forms import CustomerForm
from . models import Customer,Interaction
from django.db.models import Q
from django.core.paginator import Paginator
# Create your views here.

def home(request):
    if request.user.is_superuser:
        total_customers = Customer.objects.count()
        unassigned_customers = Customer.objects.filter(assigned_user__isnull=True).count()
        total_staff = User.objects.filter(Q(is_active=True),Q(is_superuser=False)).count()
        pending_approvals = User.objects.filter(is_active=False).count()
        total_lead_converted = Customer.objects.filter(lead_status='converted').count()
        lead_lost = Customer.objects.filter(lead_status='lost').count()

        context = {
            'total_customers':total_customers,
            'total_staff':total_staff,
            'unassigned_customers':unassigned_customers,
            'pending_approvals':pending_approvals,
            'total_lead_converted':total_lead_converted,
            'lead_lost':lead_lost,
        }
    else:
        your_customers = Customer.objects.filter(assigned_user=request.user).count()
        follow_ups = Customer.objects.filter(Q(assigned_user=request.user),Q(lead_status='follow_up')).count()
        new_lead = Customer.objects.filter(Q(assigned_user=request.user),Q(lead_status='new')).count()
        lead_lost = Customer.objects.filter(Q(assigned_user=request.user),Q(lead_status='lost')).count()
        lead_converted = Customer.objects.filter(Q(assigned_user=request.user),Q(lead_status='converted')).count()

        context ={
            'your_customers':your_customers,
            'follow_ups':follow_ups,
            'new_lead':new_lead,
            'lead_lost':lead_lost,
            'lead_converted':lead_converted,
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
    page=request.GET.get('filter','approval')
    if request.user.is_superuser:
        if page == 'approval':
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
        elif page == 'assignment':
            users = Customer.objects.filter(assigned_user__isnull=True)
            user_list = User.objects.filter(Q(is_superuser=False),Q(is_active=True))
            if request.method == 'POST':
                user_id = request.POST.get('id')
                customer_id = request.POST.get('customer_id')
                get_customer=get_object_or_404(Customer,id=customer_id)
                get_customer.assigned_user = User.objects.get(id=user_id)
                get_customer.save()
                messages.success(request,f"Assigned to {get_customer.assigned_user.username} successfully!")
            return render(request,'requests.html',{'pending_requests':users,"active_filter":page,'user_list':user_list})
    else:
        return redirect('login')
    return render(request,'requests.html',{'pending_requests':users,"active_filter":page})



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
    
    if request.method == 'POST':
        if 'new_status' in request.POST:
            updated_status_value = request.POST.get('new_status')
            customer_id = request.POST.get('customer_id')
            customer=get_object_or_404(Customer,id=customer_id)
            customer.lead_status = updated_status_value
            customer.save()
        elif 'note_body' in request.POST:
            get_note = request.POST.get('note_body')
            customer_id = request.POST.get('customer_id')
            customer = get_object_or_404(Customer,id=customer_id)
            Interaction.objects.create(
                customer = customer,
                note = get_note
            )
            previous_url = request.META.get('HTTP_REFERER')
            return redirect(previous_url)

    if request.user.is_superuser:
        customers = Customer.objects.all()
        items_per_page = 7
    else:
        customers = Customer.objects.filter(assigned_user=request.user)
        items_per_page = 6

    status_value = request.GET.get('status', 'all_category')
    customer_filter = request.GET.get('customer_filter', 'all')

    if customer_filter == 'assigned':
        customers = customers.filter(assigned_user__isnull=False)
    elif customer_filter == 'unassigned':
        customers = customers.filter(assigned_user__isnull=True)

    if status_value in ['new', 'contacted', 'follow_up', 'converted', 'lost']:
        customers = customers.filter(lead_status=status_value)

    paginator = Paginator(customers,items_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,'customer_list.html',{'customer_list':page_obj,'active_filter':customer_filter,'active_status_value':status_value})



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



def delete_customer(request,id):
    customer = get_object_or_404(Customer,id=id)
    customer.delete()
    return redirect('customer-list')