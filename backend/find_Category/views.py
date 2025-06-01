from django.shortcuts import render
import os
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings
import urllib.parse
import re
import json
import fitz
from ml import ontology


# Ensure the folder exists 
# os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

@csrf_exempt # disable csrf

def find_Type(request):
    if request.method=='POST':
        if 'resume' not in request.FILES:
            return JsonResponse({"error": "No resume file provided"},status=400)
    
        file=request.FILES['resume']
        try:
            
            resume_text=extract_text_from_pdf(file)
            # resume_text=resume_text.read().decode('utf-8',errors='ignore') # Convert file content to string
            
            print("\n\n This is resume text from find_type function: \n",resume_text)
            
        except UnicodeDecodeError:
            return JsonResponse({"error": "Could not read the file, ensure it's a text based resume"},status=400)
    
        # Matching categories
        for category, keywords in ontology.resume_categories.items():
            if any(keyword.lower() in resume_text.lower() for keyword in keywords):
                return JsonResponse({"category": category})
        return JsonResponse({"category": "Unknown Category"})
    return JsonResponse({"error": "Invalid request method"},status=405)

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    text = ""
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")  # Read from memory
    for page in pdf_document:
        text += page.get_text()
    return text.strip()