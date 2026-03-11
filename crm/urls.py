from django.urls import path
from . views import home,login_user,user_logout,register,adminDashboard,createCustomer

urlpatterns = [
    path('', home,name="home"),
    path('login/', login_user,name="login"),
    path('logout/', user_logout,name="logout"),
    path('register/', register,name="register"),
    path('admin-dashboard/',adminDashboard,name="admin-dashboard"),
    path('create-customer/',createCustomer,name="create-customer"),
]