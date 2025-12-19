from django.shortcuts import render, HttpResponse
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
from .models import *
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    return HttpResponse("<h1>Hello, world. You're at the home page.</h1><br><a href='{% url 'send_mail' %}'>Send mail</a>")

# @login_required(login_url='/')
# def send_mail(request):    
#     if request.method == 'POST':

#         subject = request.POST.get('subject', '').strip()
#         cover_letter = request.POST.get('cover_letter', '').strip()
#         recipients_raw = request.POST.get('recipients', '')
#         recipients = [r.strip() for r in recipients_raw.split(',') if r.strip()]
#         recipients = list(set(recipients))  # Remove duplicates

#         # Choose resume: either uploaded file (do NOT save to DB) or selected existing resume
#         uploaded_file = request.FILES.get('resume_file')
#         selected_resume_id = request.POST.get('resume_select')

#         # uploaded_resume_file will hold the UploadedFile when user attaches manually
#         uploaded_resume_file = None
#         resume = None

#         if uploaded_file:
#             # Do NOT save uploaded file to the Resume model; attach directly to the email
#             uploaded_resume_file = uploaded_file
#         elif selected_resume_id:
#             try:
#                 resume = Resume.objects.get(pk=selected_resume_id)
#             except Resume.DoesNotExist:
#                 return HttpResponse("Selected resume not found.", status=400)
#         else:
#             # Fall back to last saved resume in DB
#             resume = Resume.objects.last()
#             if not resume:
#                 return HttpResponse("No resume found. Please upload a resume first.<br><a href='/'>Go to Home Page</a>")


#         # TODO  HTML body rendered from template
#         # html_content = render_to_string('app/email/job_application_email.html', {
#         #     'applicant_name': applicant_name,
#         #     'applicant_email': applicant_email,
#         #     'cover_letter': cover_letter,
#         #     'resume': resume,
#         # })

#         provider_settings = settings.EMAIL_PROVIDERS.get("jobportal", {})
#         connection = get_connection(
#                         host=provider_settings["HOST"],
#                         port=provider_settings["PORT"],
#                         username=provider_settings["USER"],
#                         password=provider_settings["PASSWORD"],
#                         use_tls=provider_settings["USE_TLS"],
#                     )
#         applicant_mail = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', None) or provider_settings["USER"]

#         from_email = f"Job Application <{applicant_mail}>"
#         if not recipients:
#             return HttpResponse("Please provide at least one recipient email address.", status=400)
        
#         success_recipients = []
#         failed_recipients = []
#         parts = []
#         delivered_status = []
#         # Send HTML email using TinyMCE content as HTML body and a plain-text fallback
#         for recipient in recipients:
#             # Create plain-text fallback by stripping HTML tags from TinyMCE content
#             text_content = strip_tags(cover_letter) if cover_letter else ''
#             html_content = cover_letter or ''

#             email = EmailMultiAlternatives(
#                 subject,
#                 text_content,
#                 from_email,
#                 [recipient],
#                 connection=connection,
#             )
#             # Attach the HTML version (TinyMCE-saved HTML)
#             email.attach_alternative(html_content, "text/html")

#             # Attach the resume: prefer uploaded file (not saved), otherwise attach saved Resume.file
#             if uploaded_resume_file:
#                 # TemporaryUploadedFile exposes temporary_file_path(); InMemoryUploadedFile doesn't.
#                 try:
#                     if hasattr(uploaded_resume_file, 'temporary_file_path'):
#                         # temporary_file_path is a callable that returns the path
#                         temp_path = uploaded_resume_file.temporary_file_path()
#                         email.attach_file(temp_path)
#                     else:
#                         # In-memory file: read bytes and attach with filename and content type
#                         uploaded_resume_file.seek(0)
#                         content_type = getattr(uploaded_resume_file, 'content_type', 'application/octet-stream')
#                         email.attach(uploaded_resume_file.name, uploaded_resume_file.read(), content_type)
#                 except Exception:
#                     # Fallback: attempt to read and attach
#                     try:
#                         uploaded_resume_file.seek(0)
#                         content_type = getattr(uploaded_resume_file, 'content_type', 'application/octet-stream')
#                         email.attach(uploaded_resume_file.name, uploaded_resume_file.read(), content_type)
#                     except Exception:
#                         # If attachment fails, skip attachment but continue sending other emails
#                         pass

#             elif resume and getattr(resume, 'file', None):
#                 email.attach_file(resume.file.path)
#             # import pdb; pdb.set_trace()
#             res = email.send(fail_silently=False)
#             if res:
#                 delivered_status.append({'email': recipient, 'status': 'Sent'})
#                 success_recipients.append(recipient)
#             else:
#                 delivered_status.append({'email': recipient, 'status': 'Failed'})
#                 failed_recipients.append(recipient)


#             url = reverse('send_mail')

#         if success_recipients:
#             parts.append(f"Emails sent successfully to {', '.join(success_recipients)}.")
#         if failed_recipients:
#             parts.append(f"Failed to send to {', '.join(failed_recipients)}.")
#         BulkJobAppliedLog.objects.create(
#             total_applications = len(recipients),
#             successful_applications = len(success_recipients),
#             failed_applications = len(failed_recipients),
#             all_recievers = delivered_status,
#             sender_email = applicant_mail
#         )
#         send_another_mail = f'<a href="{url}">Send another</a>'
#         message = ' '.join(parts)

#         return render(request, 'jobportal/success.html', {
#             'message': message,
#             'success_recipients': success_recipients,
#             'failed_recipients': failed_recipients,
#             'send_another_mail': send_another_mail,
#         })

#     context = {}
#     context['resumes'] = list(Resume.objects.filter(status=True).values('name','id'))
#     context['subjects'] = list(EmailTemplate.objects.filter().values('subject','body','id'))
#     return render(request, 'jobportal/send_mail.html', context)


import threading
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from common.utils import background_email_task

# @login_required(login_url='/')
# def send_mail(request):
#     if request.method == 'POST':
#         subject = request.POST.get('subject', '').strip()
#         cover_letter = request.POST.get('cover_letter', '').strip()
#         recipients_raw = request.POST.get('recipients', '')
#         recipients = list(set([r.strip() for r in recipients_raw.split(',') if r.strip()]))

#         if not recipients:
#             return HttpResponse("Please provide at least one recipient email address.", status=400)

#         uploaded_file = request.FILES.get('resume_file')
#         selected_resume_id = request.POST.get('resume_select')
        
#         resume_path = None
#         is_temp_file = False

#         # Persistent file handling for background thread
#         if uploaded_file:
#             # Save to a temp location so the thread can access it after the request ends
#             path = default_storage.save(f'tmp/{uploaded_file.name}', ContentFile(uploaded_file.read()))
#             resume_path = os.path.join(settings.MEDIA_ROOT, path)
#             is_temp_file = True
#         elif selected_resume_id:
#             resume = Resume.objects.get(pk=selected_resume_id)
#             resume_path = resume.file.path
#         else:
#             resume = Resume.objects.last()
#             if resume:
#                 resume_path = resume.file.path

#         # Gather settings
#         provider_settings = settings.EMAIL_PROVIDERS.get("jobportal", {})
#         applicant_mail = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or provider_settings.get("USER")

#         # TRIGGER BACKGROUND THREAD
#         thread = threading.Thread(
#             target=background_email_task,
#             args=(subject, cover_letter, recipients, applicant_mail, resume_path, is_temp_file, provider_settings)
#         )
#         thread.start()

#         # Return immediate response
#         return render(request, 'jobportal/success.html', {
#             'message': f"Process started for {len(recipients)} recipients. You can check the 'Bulk Logs' once finished.",
#             'send_another_mail': f'<a href="{reverse("send_mail")}">Send another</a>',
#         })

#     # GET request logic
#     context = {
#         'resumes': list(Resume.objects.filter(status=True).values('name', 'id')),
#         'subjects': list(EmailTemplate.objects.all().values('subject', 'body', 'id'))
#     }
#     return render(request, 'jobportal/send_mail.html', context)

from django.http import JsonResponse
import uuid


@login_required(login_url='/')
def send_mail(request):
    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        cover_letter = request.POST.get('cover_letter', '').strip()
        recipients_raw = request.POST.get('recipients', '')
        recipients = list(set([r.strip() for r in recipients_raw.split(',') if r.strip()]))

        uploaded_file = request.FILES.get('resume_file')
        selected_resume_id = request.POST.get('resume_select')
        
        resume_path = None
        original_filename = "Resume.pdf"
        is_temp_file = False

        # Determine file path AND original clean name
        if uploaded_file:
            original_filename = uploaded_file.name
            filename = f"tmp_{uuid.uuid4()}_{original_filename}"
            saved_path = default_storage.save(f'temp_resumes/{filename}', ContentFile(uploaded_file.read()))
            resume_path = os.path.join(settings.MEDIA_ROOT, saved_path)
            is_temp_file = True
        elif selected_resume_id:
            res_obj = Resume.objects.get(pk=selected_resume_id)
            resume_path = res_obj.file.path
            original_filename = os.path.basename(res_obj.file.name)
        else:
            res_obj = Resume.objects.last()
            if res_obj:
                resume_path = res_obj.file.path
                original_filename = os.path.basename(res_obj.file.name)

        job_id = str(uuid.uuid4())
        provider_settings = settings.EMAIL_PROVIDERS.get("jobportal", {})
        
        BulkJobAppliedLog.objects.create(job_id=job_id, total_applications=len(recipients), sender_email=provider_settings["USER"])

        thread = threading.Thread(
            target=background_email_task,
            args=(job_id, subject, cover_letter, recipients, provider_settings["USER"], resume_path, original_filename, is_temp_file, provider_settings)
        )
        thread.start()

        return render(request, 'jobportal/success.html', {
            'job_id': job_id, 
            'count': len(recipients),
            'send_another_mail': f'<a href="{reverse("send_mail")}">Send another batch</a>'
        })

    context = {
        'resumes': list(Resume.objects.filter(status=True).values('name','id')),
        'subjects': list(EmailTemplate.objects.all().values('subject','body','id'))
    }
    return render(request, 'jobportal/send_mail.html', context)

def check_job_status(request, job_id):
    try:
        log = BulkJobAppliedLog.objects.get(job_id=job_id)
        progress = int((log.current_index / log.total_applications) * 100) if log.total_applications > 0 else 0
        return JsonResponse({
            'is_completed': log.is_completed,
            'current_index': log.current_index,
            'total_count': log.total_applications,
            'last_email': log.last_processed_email,
            'progress_percent': progress,
            'results': {
                'success': [e['email'] for e in log.all_recievers if e['status'] == 'Sent'],
                'failed': [e['email'] for e in log.all_recievers if 'Failed' in e['status']]
            }
        })
    except BulkJobAppliedLog.DoesNotExist:
        return JsonResponse({'error': 'Not Found'}, status=404)