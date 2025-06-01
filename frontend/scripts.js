
let count=0;
// localStorage.setItem('resume',`http://127.0.0.1:8000/media/software_engineer_Velocity.pdf`)
document.getElementById('resumeForm').addEventListener('submit', async function (event){
    event.preventDefault();
    console.log("Form submitted");

    // Getting required elements
    const resumeInput=document.getElementById('resume');
    const responseText=document.getElementById('response');
    const regionSelect=document.getElementById('region');
    const loadingDiv=document.getElementById('loading');

    // clear Previous messages
    responseText.innerText='';

    if(!resumeInput.files.length)
    {
        responseText.innerText="Please select a file to upload";
        return;
    }

    //Prepare form data
    const formData=new FormData();
    formData.append('resume',resumeInput.files[0]);
    formData.append('region',regionSelect.value);

    // configure fetch timeout
    // const controller=new AbortController();
    // const signal=controller.signal;
    // setTimeout(()=> controller.abort(),30000000000000);//

    try
    {
        // Disable submit button to prevent multiple submissions
        document.getElementById('submitBtn').disabled=true;

        const response=await fetch('http://127.0.0.1:8000/upload_resume/',{
            method:'POST',   
            body: formData,
            // signal
        });

        console.log("Form sent to backend");

        // Waiting for the response to fully arrive
        const result= await response.json();
        localStorage.setItem("resume",result.file_url);
        loadingDiv.classList.add('hidden'); // hidding pthe loading indicator
        
        if(response.ok)
        {
            responseText.innerText="File uploaded successfully: "+result.file_url;
            test(result.file_url);
        }
        else
        {
            console.log("response received from backend", result.error);
            responseText.innerText="Upload failed: "+result.error;
        }
    }
    catch(error)
    {
        loadingDiv.classList.add('hidden');
        console.error("Error connecting to server: ",error);
        responseText.innerText="Error: Unable to connect to server.";
    }
    finally
    {
        // Re-enable the submit button after completion
        document.getElementById('submitBtn').disabled=false;
    }
});

function test(fileURL)
{
    count++;
    const resumeEmbed=document.getElementById('resumeEmbed');
    const responseText=document.getElementById('response');
    const content=localStorage.getItem('resume');

    if(content)
    {
        console.log(content);
        resumeEmbed.src=content; // show file in an embed

        console.log(`function has run ${count}`);
        responseText.innerText="File uploaded: "+ content+ "(Run count: "+")";
        processCategory();
    }
}
test()

async function processCategory()
{
    const resumeURL=localStorage.getItem('resume');
    console.log("find the category of: ",resumeURL)
    const category=document.getElementById('category');

    if(!resumeURL)
    {
        console.error("No file URL found");
        category.innerText="Please upload a resume first";
        return;
    }
    try
    {
        // step 1: Fetch the actual file from the stored URL
        const response=await fetch(resumeURL);
        if(!response.ok) throw new Error("Failed to fetch file from URL");

        // Step 2: Convert response to a blob
        const blob=await response.blob();
        const file=new File([blob],"resume.pdf",{type: blob.type});

        // Step 3: Send the file to the backend
        const formData=new FormData();
        formData.append('resume',file); // sending the actual file not the url


        // Fetching the job category from find_category
        const apiResponse=await fetch('http://127.0.0.1:8000/find_Category/find_Type/',{
            method: 'POST',
            body: formData // Send the file using FormData
        });

        if(apiResponse.ok)
        {
            const result=await apiResponse.json();
            category.innerText="Category: "+result.category; // Display category
            console.log("Result recieved from find category function: ",result.category);
            scrapping(result.category);
        }
        else
        {
            const errorResult=await apiResponse.json();
            category.innerText="Failed to retrieve category.";
            console.error("Error: ",errorResult);
        }
    }
    catch(error)
    {
        console.error("Error couldn't find category: ", error);
        category.innerText="Unable to find category:";
    }
}

async function scrapping(category)
{
    // const category=document.getElementById('category').innerText;
    const recommendations=document.getElementById("recommendations");
    recommendations.innerText=`Jobs for ${category} are being fetched it takes some time, please wait....`;
    const region=document.getElementById('region').value;


    const formData=new FormData();
    formData.append('category',category);
    formData.append('region',region)

    try{
        // fetch the jobs scrapped from the internet
        const apiResponse=await fetch('http://127.0.0.1:8000/scrap/',{
            method: 'POST',
            body: formData
        });

        if(apiResponse.ok)
        {
            const result=await apiResponse.json();

            if (result.length>0){
                recommendations.innerHTML="<strong>Recommendation:</strong>";

                result.forEach(job => {
                    // 
                    
                    recommendations.innerHTML += `
                    <div class="card mb-3">
                        <div class="card-body">
                            <h5 class="card-title">${job.Title}</h5>
                            <p class="card-text"><strong>Company:</strong> ${job.Company}</p>
                            <p class="card-text"><strong>Location:</strong> ${job.Location}</p>
                            <a href="${job.Link}" target="_blank" class="btn btn-primary">Apply Now</a>
                        </div>
                    </div>
                `;


                });
            }else{
                recommendations.innerText=" No jobs found for this category.";
            }

            console.log("Result received from scrapper function successfully:", result);

        }else{
            const errorResult=await apiResponse.json();
            recommendations.innerText="failed to retrive jobs";
            console.error("Error: ",errorResult);   
        }
    }
    catch(error)
    {
        console.error("Error coudn't find scrap function",error);
        recommendations.innerText="Unable to scrape jobs from the internet";
    }  
    
}
