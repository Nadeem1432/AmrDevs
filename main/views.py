from django.shortcuts import render, redirect
from .models import *
from django.core.mail import send_mail, get_connection, EmailMessage
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.serializers import deserialize
from django.db import IntegrityError
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from .forms import JsonUploadForm

# Create your views here.

def index(request):
    config_data = Configuration.objects.last()
    carousel_data = Carousel.objects.filter(status=True)
    service_data = Service.objects.filter(status=True)
    project_data = Project.objects.filter(status=True)
    blog_data = Blog.objects.filter(status=True)
    team_data = TeamMember.objects.filter(status=True).order_by('id')
    client_review = ClientReview.objects.filter(status=True)
    lates_two_blogs = blog_data.only('title').order_by('-id')[:3]
    context = {
        'config': config_data,
        'carousel': carousel_data,
        'service': service_data,
        'project': project_data,
        'blog': blog_data,
        'team': team_data,
        'review': client_review,
        'posts': lates_two_blogs
    }
    return render(request, 'main/index.html',context)


def services(request):
    service_data = Service.objects.filter(status=True)
    client_review = ClientReview.objects.filter(status=True)
    config_data = Configuration.objects.last()
    lates_two_blogs = Blog.objects.filter(status=True).only('title').order_by('-id')[:3]
    context = {
        'config': config_data,
        'service': service_data,
        'review': client_review,
        'posts': lates_two_blogs
    }
    return render(request, 'main/service.html',context)

def contact(request):
    config_data = Configuration.objects.last()
    lates_two_blogs = Blog.objects.filter(status=True).only('title').order_by('-id')[:3]
    context = {
        'config': config_data,
        'posts': lates_two_blogs,
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
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

                body = full_detail
                provider_settings = settings.EMAIL_PROVIDERS.get("amrdevs")
                connection = get_connection(
                                host=provider_settings["HOST"],
                                port=provider_settings["PORT"],
                                username=provider_settings["USER"],
                                password=provider_settings["PASSWORD"],
                                use_tls=provider_settings["USE_TLS"],
                            )

                mail = EmailMessage(
                    subject='AmrDevs| Query Submission',
                    body=body,
                    from_email=provider_settings["USER"],
                    to=[provider_settings["Receiver_EMAIL"]],
                    connection=connection,
                )
                mail.send()
                context.update({'popup':"submitted",'message':f'Thank you {name}'})
                 # mail for user
                subject      = "Thank you for contact"
                user_message = "Hi "+name+",\nThank you for contact us! Our team will get back to you soon."
                user_email = EmailMessage(
                    subject=subject,
                    body=user_message,
                    from_email=provider_settings["USER"],
                    to=[email],
                    connection=connection,
                )
                user_email.send()
                return render(request, 'main/contact.html',context)
        except Exception as e:
            context.update({'popup':"failed",'message':f'Error: {e}'})
            return render(request, 'main/contact.html',context)


    return render(request, 'main/contact.html',context)

def projects(request):
    project_data = Project.objects.filter(status=True)
    config_data = Configuration.objects.last()
    lates_two_blogs = Blog.objects.filter(status=True).only('title').order_by('-id')[:3]
    context = {
        'config': config_data,
        'project': project_data,
        'posts': lates_two_blogs
    }
    return render(request, 'main/project.html',context)

def about(request):
    config_data = Configuration.objects.last()
    team_data = TeamMember.objects.filter(status=True).order_by('id')
    lates_two_blogs = Blog.objects.filter(status=True).only('title').order_by('-id')[:3]
    context = {
        'config': config_data,
        'team': team_data,
        'posts': lates_two_blogs
    }
    return render(request, 'main/about.html',context)

def team(request):
    team_data = TeamMember.objects.filter(status=True).order_by('id')
    config_data = Configuration.objects.last()
    lates_two_blogs = Blog.objects.filter(status=True).only('title').order_by('-id')[:3]
    context = {
        'config': config_data,
        'team': team_data,
        'posts': lates_two_blogs
    }
    return render(request, 'main/team.html',context)


from django.core.management import call_command
from django.http import JsonResponse

def handler(request):
    call_command('makemigrations')
    result = call_command('migrate')
    return JsonResponse({"status": "migrations applied", "result": str(result)})


@staff_member_required
def json_data_loader_view(request):
    """Custom view to handle JSON file upload and deserialization with error skipping."""
    
    if request.method == 'POST':
        form = JsonUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['json_file']
            
            # Read the file content into memory
            try:
                # Use BytesIO to handle the file content
                file_content = uploaded_file.read()
                # Assuming the file is UTF-8 encoded
                objects = list(deserialize('json', file_content.decode('utf-8')))
            except Exception as e:
                messages.error(request, f"Error reading or deserializing file: {e}")
                return render(request, 'admin/json_loader_form.html', {'form': form, 'title': 'JSON Data Loader'})

            skipped_duplicates = 0
            skipped_missing_related = 0
            saved = 0
            
            # --- CORE LOGIC FROM YOUR MANAGEMENT COMMAND ---
            for obj in objects:
                try:
                    obj.save()
                    saved += 1
                except IntegrityError:
                    skipped_duplicates += 1
                except (ContentType.DoesNotExist, ObjectDoesNotExist) as e:
                    skipped_missing_related += 1
                except Exception as e:
                    messages.warning(request, f"Unexpected error for {obj.object.__class__.__name__}: {e}")
            # --- END CORE LOGIC ---
            
            # Display results to the user
            messages.success(request, 
                f"Data Load Complete. Saved: {saved}, Skipped duplicates: {skipped_duplicates}, Skipped missing relations: {skipped_missing_related}."
            )
            # Redirect to GET to prevent form resubmission
            return redirect('json_data_loader')

    else:
        form = JsonUploadForm()

    return render(request, 'admin/json_loader_form.html', {
        'form': form,
        'title': 'JSON Data Loader',
        'site_header': 'AmrDevs Admin' # Optional: Customize admin header
    })