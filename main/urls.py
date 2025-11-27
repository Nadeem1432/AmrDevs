
from django.urls import path
from .views import *

urlpatterns = [
    path('',index, name='index'),
    path('services',services, name='services'),
    path('contact',contact, name='contact'),
    path('projects',projects, name='projects'),
    path('about',about, name='about'),
    path('team',team, name='team'),
    path('handler',handler, name='handler'),

    
]
