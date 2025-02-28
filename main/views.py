from django.shortcuts import render, HttpResponse
from .models import *
# Create your views here.

def index(request):
    config_data = Configuration.objects.last()
    carousel_data = Carousel.objects.filter(status=True)
    service_data = Service.objects.filter(status=True)
    context = {
        'config': config_data,
        'carousel': carousel_data,
        'service': service_data
    }
    return render(request, 'main/index.html',context)


def services(request):
    service_data = Service.objects.filter(status=True)
    config_data = Configuration.objects.last()
    context = {
        'config': config_data,
        'service': service_data
    }
    return render(request, 'main/service.html',context)

def contact(request):
    config_data = Configuration.objects.last()
    context = {
        'config': config_data,
    }
    return render(request, 'main/contact.html',context)

def projects(request):
    project_data = Project.objects.filter(status=True)
    config_data = Configuration.objects.last()
    context = {
        'config': config_data,
        'project': project_data
    }
    return render(request, 'main/project.html',context)

def about(request):
    config_data = Configuration.objects.last()
    context = {
        'config': config_data,
    }
    return render(request, 'main/about.html',context)

def team(request):
    team_data = TeamMember.objects.filter(status=True)
    config_data = Configuration.objects.last()
    context = {
        'config': config_data,
        'team': team_data
    }
    return render(request, 'main/team.html',context)