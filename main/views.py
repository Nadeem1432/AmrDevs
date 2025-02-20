from django.shortcuts import render, HttpResponse

# Create your views here.

def index(request):
    return render(request, 'main/index.html')
    # return HttpResponse('<h>Main page <hr> Hello, World!</h1>')
