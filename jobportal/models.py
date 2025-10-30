from django.db import models
from uuid import uuid4
from django.db import models
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from tinymce.models import HTMLField


class Resume(models.Model):
    # @staticmethod
    def filepath(instance, filename):
        # Use instance.pk when available (for existing objects); otherwise generate a temporary unique prefix
        # to avoid saving filenames containing 'None'.
        prefix = f"{instance.pk}" if instance.pk else f"{uuid4().hex}"
        return f"resumes/{prefix}/{filename}"

    name = models.CharField(max_length=100)
    file = models.FileField(upload_to=filepath)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def delete(self, using=None, keep_parents=False):
        # Ensure file removed when model is deleted programmatically or via admin
        if self.file:
            try:
                self.file.delete(save=False)
            except Exception:
                pass
        return super().delete(using=using, keep_parents=keep_parents)


# Delete file on model delete (covers other deletion paths and ensures cleanup)
@receiver(post_delete, sender=Resume)
def delete_file_on_delete(sender, instance, **kwargs):
    if instance.file:
        try:
            instance.file.delete(save=False)
        except Exception:
            pass


# Delete old file when replacing with a new file
@receiver(pre_save, sender=Resume)
def delete_old_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    old_file = old.file
    new_file = instance.file
    if old_file and old_file != new_file:
        try:
            old_file.delete(save=False)
        except Exception:
            pass

class EmailTemplate(models.Model):
    subject = models.CharField(max_length=200)
    body = HTMLField()
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.subject