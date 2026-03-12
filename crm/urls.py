from django.urls import path
from . views import home,login_user,user_logout,register,requests,create_customer,customer_list,edit_customer

urlpatterns = [
    path('', home,name="home"),
    path('login/', login_user,name="login"),
    path('logout/', user_logout,name="logout"),
    path('register/', register,name="register"),
    path('requests/',requests,name="requests"),
    path('create-customer/',create_customer,name="create-customer"),
    path('customer-list/',customer_list,name="customer-list"),
    path('edit-customer/<id>/',edit_customer,name="edit-customer"),
]
