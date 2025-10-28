from django.shortcuts import render, HttpResponse
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from .models import *

# Create your views here.
def home(request):
    return HttpResponse("<h1>Hello, world. You're at the home page.</h1><br><a href='{% url 'send_mail' %}'>Send mail</a>")


def send_mail(request):    
    if request.method == 'POST':

        subject = request.POST.get('subject', '').strip()
        cover_letter = request.POST.get('cover_letter', '').strip()
        recipients_raw = request.POST.get('recipients', '')
        recipients = [r.strip() for r in recipients_raw.split(',') if r.strip()]

        # Choose resume: either uploaded file (do NOT save to DB) or selected existing resume
        uploaded_file = request.FILES.get('resume_file')
        selected_resume_id = request.POST.get('resume_select')

        # uploaded_resume_file will hold the UploadedFile when user attaches manually
        uploaded_resume_file = None
        resume = None

        if uploaded_file:
            # Do NOT save uploaded file to the Resume model; attach directly to the email
            uploaded_resume_file = uploaded_file
        elif selected_resume_id:
            try:
                resume = Resume.objects.get(pk=selected_resume_id)
            except Resume.DoesNotExist:
                return HttpResponse("Selected resume not found.", status=400)
        else:
            # Fall back to last saved resume in DB
            resume = Resume.objects.last()
            if not resume:
                return HttpResponse("No resume found. Please upload a resume first.<br><a href='/'>Go to Home Page</a>")


        # TODO  HTML body rendered from template
        # html_content = render_to_string('app/email/job_application_email.html', {
        #     'applicant_name': applicant_name,
        #     'applicant_email': applicant_email,
        #     'cover_letter': cover_letter,
        #     'resume': resume,
        # })

        provider_settings = settings.EMAIL_PROVIDERS.get("jobportal", {})
        connection = get_connection(
                        host=provider_settings["HOST"],
                        port=provider_settings["PORT"],
                        username=provider_settings["USER"],
                        password=provider_settings["PASSWORD"],
                        use_tls=provider_settings["USE_TLS"],
                    )
        applicant_mail = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', None) or provider_settings["USER"]

        from_email = f"Job Application <{applicant_mail}>"
        if not recipients:
            return HttpResponse("Please provide at least one recipient email address.", status=400)
        
        for recipient in recipients:
            
            email = EmailMessage(
                subject,
                cover_letter,
                from_email,
                [recipient],
                connection=connection,
            )

            # Attach the resume: prefer uploaded file (not saved), otherwise attach saved Resume.file
            if uploaded_resume_file:
                # TemporaryUploadedFile exposes temporary_file_path(); InMemoryUploadedFile doesn't.
                try:
                    if hasattr(uploaded_resume_file, 'temporary_file_path'):
                        # temporary_file_path is a callable that returns the path
                        temp_path = uploaded_resume_file.temporary_file_path()
                        email.attach_file(temp_path)
                    else:
                        # In-memory file: read bytes and attach with filename and content type
                        uploaded_resume_file.seek(0)
                        content_type = getattr(uploaded_resume_file, 'content_type', 'application/octet-stream')
                        email.attach(uploaded_resume_file.name, uploaded_resume_file.read(), content_type)
                except Exception:
                    # Fallback: attempt to read and attach
                    try:
                        uploaded_resume_file.seek(0)
                        content_type = getattr(uploaded_resume_file, 'content_type', 'application/octet-stream')
                        email.attach(uploaded_resume_file.name, uploaded_resume_file.read(), content_type)
                    except Exception:
                        # If attachment fails, skip attachment but continue sending other emails
                        pass

            elif resume and getattr(resume, 'file', None):
                email.attach_file(resume.file.path)
            
            res = email.send(fail_silently=False)
            url = reverse('send_mail')
        return HttpResponse(f"Job Application Sent Successfully with response {res} <br><a href='{url}'>Go to Home Page</a>")

    context = {}
    context['resumes'] = list(Resume.objects.filter(status=True).values('name','id'))
    context['subjects'] = list(EmailTemplate.objects.filter().values('subject','body','id'))
    return render(request, 'jobportal/send_mail.html', context)
