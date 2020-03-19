from django.shortcuts import render
def api_reference(request):
    return render(request, 'rest_framework/api_reference.html')