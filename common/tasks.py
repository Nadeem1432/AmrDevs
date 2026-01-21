from celery import shared_task
import os
from jobportal.models import BulkJobAppliedLog
import mimetypes
import time
from django.core.mail import EmailMultiAlternatives, get_connection
from django.utils.html import strip_tags
from django.db import connection as db_connection


@shared_task
def background_email_task(job_id, subject, cover_letter, recipients, sender_email, resume_path, original_filename, is_temp_file, provider_settings):
    """Processes emails and attaches files using the original display name."""
    success_count = 0
    failed_count = 0
    results_list = []

    try:
        connection = get_connection(
            host=provider_settings["HOST"],
            port=provider_settings["PORT"],
            username=provider_settings["USER"],
            password=provider_settings["PASSWORD"],
            use_tls=provider_settings["USE_TLS"],
        )
        from_email = f"Job Application <{sender_email}>"
        log = BulkJobAppliedLog.objects.get(job_id=job_id)

        # Pre-read file bytes to keep the clean name during attachment
        file_data = None
        content_type = 'application/octet-stream'
        if resume_path and os.path.exists(resume_path):
            with open(resume_path, 'rb') as f:
                file_data = f.read()
            content_type, _ = mimetypes.guess_type(resume_path)
            content_type = content_type or 'application/octet-stream'

        for index, recipient in enumerate(recipients, start=1):
            log.last_processed_email = recipient
            log.save()

            text_content = strip_tags(cover_letter)
            email = EmailMultiAlternatives(subject, text_content, from_email, [recipient], connection=connection)
            email.attach_alternative(cover_letter or '', "text/html")

            # ATTACHMENT LOGIC: Restoring the clean filename
            if file_data:
                email.attach(original_filename, file_data, content_type)

            try:
                res = email.send(fail_silently=False)
                status = 'Sent' if res else 'Failed'
                if res: success_count += 1 
                else: failed_count += 1
            except Exception as e:
                status = f'Failed: {str(e)}'
                failed_count += 1

            results_list.append({'email': recipient, 'status': status})
            log.current_index = index
            log.all_recievers = results_list
            log.successful_applications = success_count
            log.failed_applications = failed_count
            log.save()
            time.sleep(1)

        log.is_completed = True
        log.save()

    finally:
        # Cleanup temporary files
        if is_temp_file and resume_path and os.path.exists(resume_path):
            os.remove(resume_path)
        db_connection.close()