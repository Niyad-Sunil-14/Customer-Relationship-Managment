from django.forms import ModelForm
from . models import Customer,User
from django.db.models import Q

class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = ['name','email','phone','company','lead_status','favorite_category','assigned_user']


    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)
        self.fields['assigned_user'].queryset = User.objects.filter(Q(is_superuser=False),Q(is_active=True))