from django.shortcuts import render

def about(request):
    return render(request, 'marketing/about.html')

def contact(request):
    return render(request, 'marketing/contact.html')
