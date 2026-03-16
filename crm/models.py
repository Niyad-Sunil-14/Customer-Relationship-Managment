from django.db import models
from django.contrib.auth.models import User
from datetime import timezone
# Create your models here.


CATEGORY_CHOICES = [
    ('product', 'Product'),
    ('services', 'Services'),
    ('real_estate', 'Real Estate'),
    ('finance', 'Finance'),
    ('tech', 'Technology'),
    ('retail', 'Retail'),
    ('other', 'Other'),
]

class Customer(models.Model):
    LEAD_STATUS = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('follow_up', 'Follow Up'),
        ('converted', 'Converted'),
        ('lost', 'Lost'),
    ]
    name =  models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.IntegerField()
    company = models.CharField(max_length=100, blank=True)
    lead_status = models.CharField(max_length=20, choices=LEAD_STATUS, default='new')
    favorite_category = models.CharField(max_length=50,choices=CATEGORY_CHOICES)
    assigned_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customers',blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



class Interaction(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='interactions'
    )
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Interaction with {self.customer.name}"