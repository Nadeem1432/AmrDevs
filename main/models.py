from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
import os
from common.utils import SupabaseCustomStorage

class GeneralFieldsMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='created_%(class)s_set',
        null=True, blank=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='updated_%(class)s_set',
        null=True, blank=True)
    status = models.BooleanField(default=True)
    misc = models.JSONField(null=True, blank=True,default=dict)
    class Meta:
        abstract = True

class SocialProfileMixin(models.Model):
    facebook = models.URLField(max_length=255, null=True, blank=True)
    twitter = models.URLField(max_length=255, null=True, blank=True)
    linkedin = models.URLField(max_length=255, null=True, blank=True)
    instagram = models.URLField(max_length=255, null=True, blank=True)
    youtube = models.URLField(max_length=255, null=True, blank=True)
    website = models.URLField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=100, null=True, blank=True) 


    class Meta:
        abstract = True

class User(AbstractUser,GeneralFieldsMixin):
    phone = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=250, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.CharField(max_length=50, null=True, blank=True)
    def __str__(self):
        return self.first_name

class TeamMember(GeneralFieldsMixin, SocialProfileMixin):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    designation = models.CharField(max_length=100)
    bio = models.TextField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='team_pictures/', null=True, blank=True)
    profile_picture_url = models.URLField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.designation}"
    
    def save(self, *args, **kwargs):
        fields_to_upload = [('profile_picture', 'team_pictures', 'profile_picture_url'),]
        if settings.PRODUCTION:
            Configuration.upload_files_to_supabase(self, fields_to_upload)
            Configuration.delete_unused_files_from_supabase(self, TeamMember, fields_to_upload)
        else:
            Configuration.delete_unused_files_from_local(self, TeamMember, fields_to_upload)
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        if settings.PRODUCTION:
            fields_to_delete = ['profile_picture_url']
            Configuration.delete_files_from_supabase(self, fields_to_delete)
        else:
            fields_to_delete = ['profile_picture']
            Configuration.delete_file_from_local(TeamMember, fields_to_delete)
        super().delete(*args, **kwargs) 


class Configuration(GeneralFieldsMixin, SocialProfileMixin):
    title = models.CharField(max_length=255)
    short_title = models.CharField(max_length=25)
    description = models.TextField(null=True, blank=True)
    newsletter = models.TextField(null=True, blank=True)
    logo = models.ImageField(upload_to='webapp_logos/', null=True, blank=True)
    favicon = models.ImageField(upload_to='webapp_favicons/', null=True, blank=True)
    bg_image = models.ImageField(upload_to='webapp_images/', null=True, blank=True)
    favicon_url = models.URLField(max_length=255, null=True, blank=True)
    bg_image_url = models.URLField(max_length=255, null=True, blank=True)
    logo_url = models.URLField(max_length=255, null=True, blank=True)
    web_link = models.URLField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=250, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.title

    @staticmethod
    def upload_files_to_supabase(instance, fields_to_upload):
        """
        Upload files to Supabase and update the corresponding URL fields.
        """
        mngr = SupabaseCustomStorage()
        for field, folder, url_field in fields_to_upload:
            file = getattr(instance, field)
            if file:
                public_url = mngr.upload_file_to_supabase(file=file, folder_path=folder, is_local_path=False)
                if not public_url:
                    raise Exception(f"{field} upload failed.")
                setattr(instance, url_field, public_url)
                setattr(instance, field, None)  # Clear the field to avoid saving the file locally

    @staticmethod
    def delete_unused_files_from_supabase(instance, model, fields_to_upload):
        mngr = SupabaseCustomStorage()
        if instance.pk is not None:
            existing_instance = model.objects.get(pk=instance.pk)
            for _, _, url_field in fields_to_upload:
                existing_url = getattr(existing_instance, url_field)
                new_url = getattr(instance, url_field)
                if existing_url and existing_url != new_url:
                    mngr.delete_file_from_supabase(existing_url)

    @staticmethod
    def delete_file_from_local(instance, fields_to_delete):
        """ Delete a local file associated with the given field of the instance.
        """
        for field in fields_to_delete:
            file = getattr(instance, field)
            if file:
                try:
                    if os.path.isfile(file.path):
                        os.remove(file.path)
                    else:
                        print(f"File not found: {file.path}")
                except Exception as e:
                    print(f"Error deleting file: {e}")

    @staticmethod
    def delete_files_from_supabase(instance, fields_to_delete):
        """
        Delete files from Supabase based on the provided URL fields.
        """
        mngr = SupabaseCustomStorage()
        for url_field in fields_to_delete:
            url = getattr(instance, url_field)
            if url:
                try:
                    mngr.delete_file_from_supabase(url)
                except Exception as e:
                    print(f"Error deleting file from Supabase: {e}")

    @staticmethod
    def delete_unused_files_from_local(instance, model, fields_to_delete):
        if instance.pk is not None:
            existing_instance = model.objects.get(pk=instance.pk)
            for field ,_ ,_  in fields_to_delete:
                existing_file = getattr(existing_instance, field)
                new_file = getattr(instance, field)
                if existing_file and existing_file != new_file:
                    try:
                        if os.path.isfile(existing_file.path):
                            os.remove(existing_file.path)
                        else:
                            print(f"File not found: {existing_file.path}")
                    except Exception as e:
                        print(f"Error deleting file: {e}")

    def save(self, *args, **kwargs):
        fields_to_upload = [
            ('favicon', 'favicons', 'favicon_url'),
            ('logo', 'logos', 'logo_url'),
            ('bg_image', 'bg_images', 'bg_image_url'), ]

        if settings.PRODUCTION:
            self.upload_files_to_supabase(self, fields_to_upload) # Upload new files to Supabase
            self.delete_unused_files_from_supabase(self, Configuration, fields_to_upload) # Delete unused files from Supabase
        else:
            self.delete_unused_files_from_local(self, Configuration, fields_to_upload) # Delete unused local files
        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        if settings.PRODUCTION:
            fields_to_delete = ['favicon_url', 'logo_url', 'bg_image_url']
            self.delete_files_from_supabase(self, fields_to_delete)  # Delete files from Supabase
        else:
            fields_to_delete = ['favicon','logo', 'bg_image']
            self.delete_file_from_local(self, fields_to_delete)  # Delete local file
        super().delete(using, keep_parents)

class ClientReview(GeneralFieldsMixin):
    client_name = models.CharField(max_length=255)
    client_photo = models.ImageField(upload_to='client_photos/', null=True, blank=True)
    client_photo_url = models.URLField(max_length=255, null=True, blank=True)
    client_profession = models.CharField(max_length=255, null=True, blank=True)
    review = models.TextField()
    rating = models.PositiveIntegerField(default=5)
    project = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.client_name} - {self.rating}/5"
    
    def delete(self, *args, **kwargs):
        if settings.PRODUCTION:
            fields_to_delete = ['client_photo_url']
            Configuration.delete_files_from_supabase(self, fields_to_delete)
        else:
            fields_to_delete = ['client_photo']
            Configuration.delete_file_from_local(ClientReview, fields_to_delete)

        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        fields_to_upload = [('client_photo', 'client_photos', 'client_photo_url'),]
        if settings.PRODUCTION:
            Configuration.upload_files_to_supabase(self, fields_to_upload)
            Configuration.delete_unused_files_from_supabase(self, ClientReview, fields_to_upload)
        else:
            Configuration.delete_unused_files_from_local(self, ClientReview, fields_to_upload)
        super().save(*args, **kwargs)

class Blog(GeneralFieldsMixin):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    published_date = models.DateTimeField(default=timezone.now)
    cover_image = models.ImageField(upload_to='blog_covers/', null=True, blank=True)
    cover_image_url = models.URLField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.title
    
    def delete(self, *args, **kwargs):
        if settings.PRODUCTION:
            fields_to_delete = ['cover_image_url']
            Configuration.delete_files_from_supabase(self, fields_to_delete)
        else:
            fields_to_delete = ['cover_image']
            Configuration.delete_file_from_local(Blog, fields_to_delete)

        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        fields_to_upload = [ ('cover_image', 'blog_covers', 'cover_image_url'),]
        if settings.PRODUCTION:
            Configuration.upload_files_to_supabase(self, fields_to_upload)
            Configuration.delete_unused_files_from_supabase(self, Blog, fields_to_upload)
        else:
            Configuration.delete_unused_files_from_local(self, Blog, fields_to_upload)
        super().save(*args, **kwargs)
    
class Service(GeneralFieldsMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='service_images/', null=True, blank=True)
    image_url = models.URLField(max_length=255, null=True, blank=True)
    link = models.URLField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        fields_to_upload = [ ('image', 'service_images', 'image_url'),]
        if settings.PRODUCTION:
            Configuration.upload_files_to_supabase(self, fields_to_upload)
            Configuration.delete_unused_files_from_supabase(self, Service, fields_to_upload)
        else:
            Configuration.delete_unused_files_from_local(self, Service, fields_to_upload)

        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        if settings.PRODUCTION:
            fields_to_delete = ['image_url']
            Configuration.delete_files_from_supabase(self, fields_to_delete)
        else:
            fields_to_delete = ['image']
            Configuration.delete_file_from_local(Service, fields_to_delete)    
        super().delete(*args, **kwargs)

class Conversation(GeneralFieldsMixin):
    sender_name = models.CharField(max_length=255)
    sender_email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    response_status = models.CharField(max_length=50, null=True, blank=True)
    response_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.sender_name} - {self.subject}"

class Project(GeneralFieldsMixin):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='project_images/', null=True, blank=True)
    image_url = models.URLField(max_length=255, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    client = models.CharField(max_length=255, null=True, blank=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    work_status = models.CharField(max_length=50, choices=[('ongoing', 'Ongoing'), ('completed', 'Completed'), ('on_hold', 'On Hold')], default='ongoing')

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        fields_to_upload = [ ('image', 'project_images', 'image_url'),]
        if settings.PRODUCTION:
            Configuration.upload_files_to_supabase(self, fields_to_upload)
            Configuration.delete_unused_files_from_supabase(self, Project, fields_to_upload)
        else:
            Configuration.delete_unused_files_from_local(self, Project, fields_to_upload)
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        if settings.PRODUCTION:
            fields_to_delete = ['image_url']
            Configuration.delete_files_from_supabase(self, fields_to_delete)
        else:
            fields_to_delete = ['image']
            Configuration.delete_file_from_local(Project, fields_to_delete)
        super().delete(*args, **kwargs)

class Carousel(GeneralFieldsMixin):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='carousel_images/')
    image_url = models.URLField(max_length=255, null=True, blank=True)
    link = models.URLField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        fields_to_upload = [ ('image', 'carousel_images', 'image_url'),]
        if settings.PRODUCTION:
            Configuration.upload_files_to_supabase(self, fields_to_upload)
            Configuration.delete_unused_files_from_supabase(self, Carousel, fields_to_upload)
        else:
            Configuration.delete_unused_files_from_local(self, Carousel, fields_to_upload)
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        if settings.PRODUCTION:
            fields_to_delete = ['image_url']
            Configuration.delete_files_from_supabase(self, fields_to_delete)
        else:
            fields_to_delete = ['image']
            Configuration.delete_file_from_local(Carousel, fields_to_delete)

        super().delete(*args, **kwargs)

    class Meta:
        ordering = ['id']