# urls.py
from django.urls import path
from .views import add_event,events_list

urlpatterns = [
    path('add_event/', add_event, name='add_event'),
    path('events_list/', events_list, name='events_list'),
]
