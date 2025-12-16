"""
URL configuration for amrdevs project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# # --- SITEMAP IMPORTS ---
# from django.contrib.sitemaps.views import sitemap
# # Import your sitemap class (adjust the import path if sitemaps.py is elsewhere)
# from main.sitemaps import StaticViewSitemap 

# # --- SITEMAP DEFINITION ---
# # A dictionary mapping a key (e.g., 'static') to the sitemap class
# sitemaps = {
#     'static': StaticViewSitemap,
# }


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('', include('main.urls')),
    path('panel/', include('panel.urls')),
    path('job-portal/', include('jobportal.urls')),
    path('tinymce/', include('tinymce.urls')),

] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

