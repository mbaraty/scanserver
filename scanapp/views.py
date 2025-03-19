import shutil
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import File
from pdf2image import convert_from_path
import numpy as np
import cv2
import pytesseract
import ollama
import pandas as pd
from django.core.files import File as DjangoFile
import os
from django.conf import settings

import os


SCAN_PATH = "/mnt/scanserver-files/input/"
SHARE_PATH = "/mnt/scanserver-files/"

prompt = ("this text was extracted from a pdf document. Give me a description of what the document could be about that "
          "is capped at 150 characters. dont reference the document; does not ened to be a cmoplete sentence. "
          "Example: a home depot receipt containing purchase of a hammer and a drill on 10/3/2032.")


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
    client = ollama.Client("http://desktop-rlieigr:11434")
    now = timezone.now()
    target_dir = f'docs/{now.year}/{now.month}/{now.day}/'
    os.makedirs(SHARE_PATH + target_dir, exist_ok=True)
    fname = f'{target_dir}{now.time()}'
    target_path = f'{fname}.pdf'
    target_txt = f'{fname}.txt'
    full_path = SCAN_PATH + name

    os.rename(full_path, SHARE_PATH + target_path)
    text = process_text_from_file(SHARE_PATH + target_path)
    with open(SHARE_PATH + target_txt, 'w') as f:
        f.write(text)
    response = client.generate(model="llama3.2", prompt=prompt + "\n" + text)
    print(response["response"])

    # Save relative path to the DB
    File.objects.create(date_created=now, path=target_path, hidden=False, text_path=target_txt, description=response["response"])



## thanks to
# https://medium.com/@dr.booma19/extracting-text-from-pdf-files-using-ocr-a-step-by-step-guide-with-python-code-becf221529ef
def process_text_from_file(path):
    pages = convert_from_path(path)

    # Create a list to store extracted text from all pages
    extracted_text = ""

    target_dir = path + ".d"
    os.makedirs(target_dir, exist_ok=True)
    target_dir += '/'
    for idx, page in enumerate(pages):
        # Step 2: Preprocess the image (deskew)
        preprocessed_image = page #deskew(np.array(page))

        # cv2.imwrite(target_dir + str(idx) + ".jpg", preprocessed_image)
        page.save(target_dir + str(idx) + ".jpg")


        # Step 3: Extract text using OCR
        text = extract_text_from_image(preprocessed_image)
        extracted_text = extracted_text + "\n" + text

    return extracted_text


def deskew(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)
    coords = np.column_stack(np.where(gray > 0))
    angle = cv2.minAreaRect(coords)[-1]

    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return rotated


def extract_text_from_image(image):
    text = pytesseract.image_to_string(image, config="-c preserve_interword_spaces=1")
    return text


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
    file = get_object_or_404(File, pk=pk)
    return render(request, "file.html", {"file": file})


def download_pdf(request, pk):
    name = request.POST["name"]
    filename = name if name.endswith(".pdf") else name + ".pdf"
    file = get_object_or_404(File, pk=pk)
    response = HttpResponse(file.path, content_type='application/force-download')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    file.hidden = True
    file.save()
    return response


def download_jpg(request, pk):
    name = request.POST["name"]
    file = get_object_or_404(File, pk=pk)
