from django.forms import ModelForm
from . models import Customer

class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = ['name','email','phone','company','lead_status','favorite_category','assigned_user']