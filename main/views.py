from django.shortcuts import render, HttpResponse
from .models import *
# Create your views here.

def index(request):
    config_data = Configuration.objects.last()
    carousel_data = Carousel.objects.filter(status=True)
    service_data = Service.objects.filter(status=True)
    project_data = Project.objects.filter(status=True)
    blog_data = Blog.objects.filter(status=True)
    team_data = TeamMember.objects.filter(status=True)
    client_review = ClientReview.objects.filter(status=True)
    context = {
        'config': config_data,
        'carousel': carousel_data,
        'service': service_data,
        'project': project_data,
        'blog': blog_data,
        'team': team_data,
        'review': client_review
    }
    print("test")
    return render(request, 'main/index.html',context)


def services(request):
    service_data = Service.objects.filter(status=True)
    client_review = ClientReview.objects.filter(status=True)
    config_data = Configuration.objects.last()
    context = {
        'config': config_data,
        'service': service_data,
        'review': client_review
    }
    return render(request, 'main/service.html',context)
from django.core.mail import send_mail
def contact(request):
    config_data = Configuration.objects.last()
    context = {
        'config': config_data,
    }
    if request.method == 'POST':
        try:
            if request.POST['name'] and request.POST['email'] and request.POST['subject'] and request.POST['message'] and request.POST['phone']:
                name 	= request.POST['name']
                email   = request.POST['email']
                phone   = request.POST['phone']
                sender_subject   = request.POST['subject']
                message = request.POST['message']
                # mail for us
                full_detail =" \n\n"+  message + " \n\n\n\n" +  "Name: "+ name +" \n"+    "Email: "+ email +" \n"+    "Phone: "+ phone+  " \n"+  "Query: "+ sender_subject
                send_mail('Amrohvi Developers',     #subject
                                full_detail, #message
                                settings.EMAIL_HOST_USER, #sender_email
                                ['nadeemali2502@gmail.com'],  #receiver_email
                                fail_silently=False)
                # mail for user
                subject      = "Thank you for contact"
                user_message = "Hi "+name+",Thank you for contact us! our team will get back to you soon."
                send_mail(subject,
                                user_message,
                                settings.EMAIL_HOST_USER,
                                [email],
                                fail_silently=False)
                context.update({'popup':"submitted",'message':f'Thank you {name}'})

                return render(request, 'main/contact.html',context)
        except Exception as e:
            context.update({'popup':"failed",'message':f'Error: {e}'})
            return render(request, 'main/contact.html',context)


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
    team_data = TeamMember.objects.filter(status=True)
    context = {
        'config': config_data,
        'team': team_data,
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