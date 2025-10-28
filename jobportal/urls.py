from django.urls import path, include
from .views import *
urlpatterns = [
    # path('', home, name='home'),
    path('', send_mail, name='send_mail')
]
