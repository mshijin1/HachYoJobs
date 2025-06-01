from django.shortcuts import render
import os
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings
import urllib.parse
import re
import json
import fitz  # PyMuPDF for PDF extraction
from django.core.cache import cache

# Ensure the folder exists 
# os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

@csrf_exempt # disable csrf

def upload_resume(request):
    if request.method=='POST' or request.method=='GET':
        
        print("Request method received:", request.method)
        print("Request body:", request.body)
        print("Request POST keys:", request.POST.keys())
        print("Request FILES keys:", request.FILES.keys())
        
    
        # Checking if the file is present in the request
        if 'resume' not in request.FILES:
            return JsonResponse({'error':'No resume file provided'}, status=400)
        
        uploaded_file=request.FILES['resume']
        
        
        print("The uploaded file is: ", uploaded_file)
        
        region=request.POST['region']
        
        # Save the file in the data/resumes folder
        # save_path=os.path.join(settings.MEDIA_ROOT,uploaded_file.name)
        clean_file_name = uploaded_file.name.replace(" ", "_")


        clean_file_name = re.sub(r'\s+', '_', clean_file_name)  # Replace multiple spaces with a single underscore
        clean_file_name = re.sub(r'[^a-zA-Z0-9_.-]', '', clean_file_name)  # Remove special characters except underscores and dots
        
        
        print("Clean file name is: \n",clean_file_name)
        
        file_extension =clean_file_name.split('.')[-1].lower()  # Get file extension
        print("file extension is :", file_extension)
        
        if file_extension == "pdf":
            resume_text = extract_text_from_pdf(uploaded_file)
            
            resume_text=re.sub('http\S+\s',' ',resume_text)
            resume_text=re.sub('RT|cc',' ',resume_text)
            resume_text=re.sub('@\S+',' ',resume_text)
            resume_text=re.sub('#\S+\s',' ',resume_text)
            resume_text=re.sub('[%s]'% re.escape("""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""),' ',resume_text)
            resume_text=re.sub(r'[^\x00-\x7f]',' ',resume_text)
            resume_text=re.sub('\s+',' ',resume_text)
            resume_text=re.sub(r'\r\n\r\\', ' ', resume_text)    
            resume_text = f"\n my resume content: \n{resume_text}"
            # print(resume_text)
            
           
            cache.set('resume_text', resume_text, timeout=3600)  # Store for 1 hour
            
        

        save_path=os.path.join(settings.MEDIA_ROOT,clean_file_name)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        print("Resume saved at:",save_path)
        
        
        with open(save_path,'wb') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)
        
            
            file_url=request.build_absolute_uri(settings.MEDIA_URL + clean_file_name)
            print("file URL  sent to the frontend : ",file_url)
            print("URL name: ",clean_file_name)
            
            
            # return JsonResponse({'message':'Resume uploaded successfully', 'region':region, 'file_url':file_url}, status=200)

            # JavaScript code to save the file_url in localStorage
            script = f"""
            <script>
                localStorage.removeItem(resume);
                localStorage.setItem('resume', '{file_url}');
                console.log('File URL saved in localStorage:', localStorage.getItem('resume'));
            </script>
            """
            return JsonResponse({'message': 'Resume uploaded successfully','region': region, 'file_url': file_url, 'script': script}, status=200)
            
            # # return the saved file directly in response
            # return FileResponse(open(save_path, 'rb'), content_type='application/pdf')
    
    return JsonResponse({"error":"Invalid request method"},status=405)   



# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    text = ""
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")  # Read from memory
    for page in pdf_document:
        text += page.get_text()
    return text.strip()