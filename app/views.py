from django.shortcuts import render
from django.http import JsonResponse

def ytdownload(request):
    return render(request, 'ytdownload.html', {'video_url': ''})