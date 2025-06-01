
from django.shortcuts import render
import os
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings
import urllib.parse
import re
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.common.action_chains import ActionChains
from LSA import rank_jobs_by_relevance

from resume_uploads.views import upload_resume

import json
import time
import csv
import re
import sqlite3
import pdb
from django.core.cache import cache


@csrf_exempt # disable csrf
def scrap(request):
   resume_text = cache.get('resume_text')
   if resume_text:
       print("\n\nYes now we can access resume_text\n\n")
   if not resume_text:
        return JsonResponse({'error': 'Resume text not found. Please upload a resume first.'}, status=400)


   if request.method!='POST':
       return JsonResponse({'error':'Only POST allowed'})
   
   if request.method =='POST':
          # Checking if the file is present in the request
        if 'category' not in request.POST or 'region' not in request.POST:
            return JsonResponse({'error':'Missing category or region'}, status=400)
        
        category=request.POST['category']
        region=request.POST['region']
        
        
        # setting up Chrome options
        chrome_options=Options()
        chrome_options.add_argument("--headless") # for running chrome without UI
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36")

        service=Service(r'C:\Users\ACER\Downloads\chromedriver-win64 (1)\chromedriver-win64\chromedriver.exe')
        driver=webdriver.Chrome(service=service,options=chrome_options)

   try:
        # load the webpage
        driver.get(f"https://www.freshersworld.com/jobs/jobsearch/{category}-jobs-in-{region}")
        
        # Wait for the url to load the element
        WebDriverWait(driver, 40).until(
            EC.presence_of_all_elements_located((By.XPATH,".//div[contains(@class,'col-md-12 col-lg-12 col-xs-12 padding-none job-container jobs-on-hover top_space')]"))
        )
        print('this page is accessible')
        
        # finding a job cards
        job_cards=driver.find_elements(By.XPATH,".//div[contains(@class,'col-md-12 col-lg-12 col-xs-12 padding-none job-container jobs-on-hover top_space')]")
        print(f"Found {len(job_cards)} job cards.")  # Debugging: Check how many cards are found
        
        # current page url
        current_url=driver.current_url
        
        logged_links=[]
        Job_listings=[]
        for i in range(len(job_cards)):
            try:
                driver.refresh()
                job_cards=driver.find_elements(By.XPATH,".//div[contains(@class,'col-md-12 col-lg-12 col-xs-12 padding-none job-container jobs-on-hover top_space')]")
                job=job_cards[i]
                # Move to the job element
                ActionChains(driver).move_to_element(job).perform() 
                
                # Title
                title=job.find_element(By.XPATH,".//span[contains(@class,'seo_title')]").text
                
                # company
                company=job.find_element(By.XPATH,".//h3[contains(@class,'latest-jobs-title font-16 margin-none inline-block company-name')]").text
                
                # location
                location=job.find_element(By.XPATH,".//a[contains(@class,'bold_font')]").text
        
                
                # Experience
                Experience=job.find_element(By.XPATH,".//span[contains(@class,'experience job-details-span')]").text
        
                description=""
                try:
                    # description
                    link=job.get_attribute('job_display_url')
                    
                    print(f"Processing job {i + 1}: {link}")  # Log the link for debugging
                    logged_links.append(link)
                    
                    driver.get(link)
                    
                    WebDriverWait(driver, 40).until(
                        EC.presence_of_all_elements_located((By.XPATH,".//div[contains(@class,'job-desc')]"))
                    )
                    
                    description=driver.find_element(By.XPATH,".//div[contains(@class,'job-desc')]").text
                    description=re.sub('http\S+\s',' ',description)
                    description=re.sub('RT|cc',' ',description)
                    description=re.sub('@\S+',' ',description)
                    description=re.sub('#\S+\s',' ',description)
                    description=re.sub('[%s]'% re.escape("""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""),' ',description)
                    description=re.sub(r'[^\x00-\x7f]',' ',description)
                    description=re.sub('\s+',' ',description)
                    description=re.sub(r'\r\n\r\\', ' ', description)    
                    
                except Exception as e:
                    print(f"some problem")
                
                driver.get(current_url)
                WebDriverWait(driver, 20).until(
                    EC.presence_of_all_elements_located((By.XPATH,".//div[contains(@class,'col-md-12 col-lg-12 col-xs-12 padding-none job-container jobs-on-hover top_space')]"))
                )
                
                # job_cards = driver.find_elements(By.XPATH, ".//div[contains(@class,'col-md-12 col-lg-12 col-xs-12 padding-none job-container jobs-on-hover top_space')]")
                
                Job_listings.append({
                    'Title': title,
                    'Company': company,
                    'Location': location,
                    'Experience':Experience,
                    'Description':description,
                    'Link':link
                    }) 
                
            except Exception as e:
                print(f"An error occurred: This indicates that the job card may not be accessible or the element is not found.")
                
        sorted_Job_listings=rank_jobs_by_relevance(resume_text,Job_listings)
        if sorted_Job_listings:
            print(" \n\n We have sorted job listings now")
        else:
            print("\n\n we could perform LSA \n\n")
        
        # print(json.dumps(Job_listings,indent=4))
        return JsonResponse(sorted_Job_listings, safe=False)

   finally:
        driver.quit()
    
    
    
    
    
    



    
    
# from django.shortcuts import render
# import os
# from django.http import JsonResponse, FileResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.core.files.storage import default_storage
# from django.conf import settings
# import urllib.parse
# import re
# import json
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC 
# from selenium.webdriver.common.action_chains import ActionChains
# from LSA import rank_jobs_by_relevance

# from resume_uploads.views import upload_resume

# import json
# import time
# import csv
# import re
# import sqlite3
# import pdb
# from django.core.cache import cache


# @csrf_exempt # disable csrf
# def scrap(request):
#    resume_text = cache.get('resume_text')
#    if resume_text:
#        print("\n\nYes now we can access resume_text\n\n")
#    if not resume_text:
#         return JsonResponse({'error': 'Resume text not found. Please upload a resume first.'}, status=400)
    
#    if request.method =='POST':
#           # Checking if the file is present in the request
#         if 'category' not in request.POST or 'region' not in request.POST:
#             return JsonResponse({'error':'Missing category or region'}, status=400)
        
#         category=request.POST['category']
#         region=request.POST['region']
        
        
#         # setting up Chrome options
#         chrome_options=Options()
#         chrome_options.add_argument("--headless") # for running chrome without UI
#         chrome_options.add_argument("--disable-gpu")
#         chrome_options.add_argument("--no-sandbox")
#         chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36")

#         service=Service(r'C:\\Users\ACER\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe')
#         driver=webdriver.Chrome(service=service,options=chrome_options)

#    try:
#         # load the webpage
#         driver.get(f"https://www.freshersworld.com/jobs/jobsearch/{category}-jobs-in-{region}")
        
#         # Wait for the url to load the element
#         WebDriverWait(driver, 40).until(
#             EC.presence_of_all_elements_located((By.XPATH,".//div[contains(@class,'col-md-12 col-lg-12 col-xs-12 padding-none job-container jobs-on-hover top_space')]"))
#         )
#         print('this page is accessible')
        
#         # finding a job cards
#         job_cards=driver.find_elements(By.XPATH,".//div[contains(@class,'col-md-12 col-lg-12 col-xs-12 padding-none job-container jobs-on-hover top_space')]")
#         print(f"Found {len(job_cards)} job cards.")  # Debugging: Check how many cards are found
        
#         # current page url
#         current_url=driver.current_url
        
#         logged_links=[]
#         Job_listings=[]
#         for i in range(len(job_cards)):
#             try:
#                 driver.refresh()
#                 job_cards=driver.find_elements(By.XPATH,".//div[contains(@class,'col-md-12 col-lg-12 col-xs-12 padding-none job-container jobs-on-hover top_space')]")
#                 job=job_cards[i]
#                 # Move to the job element
#                 ActionChains(driver).move_to_element(job).perform() 
                
#                 # Title
#                 title=job.find_element(By.XPATH,".//span[contains(@class,'seo_title')]").text
                
#                 # company
#                 company=job.find_element(By.XPATH,".//h3[contains(@class,'latest-jobs-title font-16 margin-none inline-block company-name')]").text
                
#                 # location
#                 location=job.find_element(By.XPATH,".//a[contains(@class,'bold_font')]").text
        
                
#                 # Experience
#                 Experience=job.find_element(By.XPATH,".//span[contains(@class,'experience job-details-span')]").text
        
#                 description=""
#                 try:
#                     # description
#                     link=job.get_attribute('job_display_url')
                    
#                     print(f"Processing job {i + 1}: {link}")  # Log the link for debugging
#                     logged_links.append(link)
                    
#                     driver.get(link)
                    
#                     WebDriverWait(driver, 40).until(
#                         EC.presence_of_all_elements_located((By.XPATH,".//div[contains(@class,'job-desc')]"))
#                     )
                    
#                     description=driver.find_element(By.XPATH,".//div[contains(@class,'job-desc')]").text
#                     description=re.sub('http\S+\s',' ',description)
#                     description=re.sub('RT|cc',' ',description)
#                     description=re.sub('@\S+',' ',description)
#                     description=re.sub('#\S+\s',' ',description)
#                     description=re.sub('[%s]'% re.escape("""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""),' ',description)
#                     description=re.sub(r'[^\x00-\x7f]',' ',description)
#                     description=re.sub('\s+',' ',description)
#                     description=re.sub(r'\r\n\r\\', ' ', description)    
                    
#                 except Exception as e:
#                     print(f"some problem")
                
#                 driver.get(current_url)
#                 WebDriverWait(driver, 20).until(
#                     EC.presence_of_all_elements_located((By.XPATH,".//div[contains(@class,'col-md-12 col-lg-12 col-xs-12 padding-none job-container jobs-on-hover top_space')]"))
#                 )
                
#                 # job_cards = driver.find_elements(By.XPATH, ".//div[contains(@class,'col-md-12 col-lg-12 col-xs-12 padding-none job-container jobs-on-hover top_space')]")
                
#                 Job_listings.append({
#                     'Title': title,
#                     'Company': company,
#                     'Location': location,
#                     'Experience':Experience,
#                     'Description':description,
#                     'Link':link
#                     }) 
                
#             except Exception as e:
#                 print(f"An error occurred: {e}")
                
#         sorted_Job_listings=rank_jobs_by_relevance(resume_text,Job_listings)
#         if sorted_Job_listings:
#             print(" \n\n We have sorted job listings now")
#         else:
#             print("\n\n we could perform LSA \n\n")
        
#         # print(json.dumps(Job_listings,indent=4))
#         return JsonResponse(sorted_Job_listings, safe=False)

#    finally:
#         driver.quit()