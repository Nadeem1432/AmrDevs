from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.urls import resolve, Resolver404

class Custom404Middleware:
    """
    Handles 404 pages even when DEBUG=True.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            # Try resolving the URL first
            resolve(request.path_info)
        except Resolver404:
            # If no match found, render 404.html
            return render(request, "main/404.html", status=404)
        return self.get_response(request)
