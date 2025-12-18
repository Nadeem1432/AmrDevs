from django.urls import path, include
from .views import *
# urlpatterns = [
#     path('', send_mail, name='send_mail')
# ]

urlpatterns = [
    path('', send_mail, name='send_mail'),
    path('check-status/<str:job_id>/', check_job_status, name='check_job_status'),
]
