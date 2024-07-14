# urls.py
from django.urls import path
from .views import add_event,events_list,home,signup,login,dashboard,users,toggle_staff,toggle_superuser,logout,forgot_password

urlpatterns =[
    path('',home,name="home"),
    path('signup',signup,name='signup'),
    path('login/',login,name='login'),
    path('logout',logout,name='logout'),
    path('forgot_password',forgot_password,name="forgot_password"),
    path('reset/<uidb64>/<token>/',forgot_password, name='password_reset_confirm'),
    path('users',users,name='users'),
    path('dashboard',dashboard,name='dashboard'),
    path('add_event/', add_event, name='add_event'),
    path('events_list/', events_list, name='events_list'),
    path('toggle_staff/<int:user_id>/', toggle_staff, name='toggle_staff'),
    path('toggle_superuser/<int:user_id>/', toggle_superuser, name='toggle_superuser'),
]
