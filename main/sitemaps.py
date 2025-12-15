from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    # These settings apply to all static pages listed in the items method.
    # We set a high priority for core business pages.
    changefreq = "weekly" 
    priority = 0.8 

    def items(self):
        """
        Returns a list of view names that should be included in the sitemap.
        These names MUST exactly match the 'name=' argument in your app's urls.py.
        """
        return [
            'index',
            'services',
            'contact',
            'projects',
            'about',
            'team',
            
            # NOTE: 'handler' is excluded as it's typically a submission endpoint, not content.
            # Add 'privacy_policy' or 'terms_of_service' if you create those named paths.
        ]

    def location(self, item):
        """
        Generates the absolute URL for each item using the view name.
        """
        return reverse(item)

# If you were to add models later (like 'jobportal' entries), 
# you would define additional sitemap classes here and add them to the 
# sitemaps dictionary in your project's urls.py.