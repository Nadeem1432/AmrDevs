from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone

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

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.designation}"
    

class Configuration(GeneralFieldsMixin, SocialProfileMixin):
    title = models.CharField(max_length=255)
    short_title = models.CharField(max_length=25)
    description = models.TextField(null=True, blank=True)
    newsletter = models.TextField(null=True, blank=True)
    logo = models.ImageField(upload_to='webapp_logos/', null=True, blank=True)
    favicon = models.ImageField(upload_to='webapp_favicons/', null=True, blank=True)
    bg_image = models.ImageField(upload_to='webapp_images/', null=True, blank=True)
    web_link = models.URLField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=250, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.title
    
class ClientReview(GeneralFieldsMixin):
    client_name = models.CharField(max_length=255)
    client_photo = models.ImageField(upload_to='client_photos/', null=True, blank=True)
    client_profession = models.CharField(max_length=255, null=True, blank=True)
    review = models.TextField()
    rating = models.PositiveIntegerField(default=5)
    project = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.client_name} - {self.rating}/5"
    
class Blog(GeneralFieldsMixin):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    published_date = models.DateTimeField(default=timezone.now)
    cover_image = models.ImageField(upload_to='blog_covers/', null=True, blank=True)

    def __str__(self):
        return self.title
    
class Service(GeneralFieldsMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='service_images/', null=True, blank=True)
    link = models.URLField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name
    
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
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    client = models.CharField(max_length=255, null=True, blank=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    work_status = models.CharField(max_length=50, choices=[('ongoing', 'Ongoing'), ('completed', 'Completed'), ('on_hold', 'On Hold')], default='ongoing')

    def __str__(self):
        return self.title
    
class Carousel(GeneralFieldsMixin):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='carousel_images/')
    link = models.URLField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['id']