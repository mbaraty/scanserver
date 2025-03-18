import shutil
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import File
from django.core.files import File as DjangoFile
import os
from django.conf import settings

import os

SCAN_PATH = "/mnt/scanserver-files/input/"
SHARE_PATH = "/mnt/scanserver-files/"


def list_new_files():
    files = os.listdir(SCAN_PATH)
    return files
    
def list_visible_processed_files():
    files = File.objects.filter(hidden=False).order_by("-date_created")
    return list(files)

def list_hidden_files():
    files = File.objects.filter(hidden=True).order_by("-date_created")
    return files
    
def process_file(name):
    now = timezone.now()
    target_dir = f'docs/{now.year}/{now.month}/{now.day}/'
    os.makedirs(SHARE_PATH + target_dir, exist_ok=True)
    
    target_path = f'{target_dir}{now.time()}.pdf'
    full_path = SCAN_PATH + name

    os.rename(full_path, SHARE_PATH + target_path)

    # Save relative path to the DB
    File.objects.create(date_created=now, path=target_path, hidden=False)

# Create your views here.
def index(request):
    for file in list_new_files():
        process_file(file)
    l = list_visible_processed_files()
    return render(request, "index.html", {"list": l})

def hidden(request):
    l = list_hidden_files()
    return render(request, "hidden.html", {"list": l})

def file(request, pk):
    file = get_object_or_404(File,pk=pk)
    return render(request, "file.html", {"file": file})

def download_pdf(request, pk):
    name = request.POST["name"]
    filename = name if name.endswith(".pdf") else name + ".pdf"
    file = get_object_or_404(File,pk=pk)
    response = HttpResponse(file.path, content_type='application/force-download')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    file.hidden = True
    file.save()
    return response

def download_jpg(request, pk):
    name = request.POST["name"]

