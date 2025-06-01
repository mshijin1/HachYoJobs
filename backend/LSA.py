import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns 
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity


def rank_jobs_by_relevance(resume: str, job_listings: list):
    
    # Extract job descriptions
    job_descriptions=[job['Description'] for job in job_listings]
    
    # Combine job description with resume for vectorization
    text=[resume] + job_descriptions
    
    # Convert text to numerical dat using Tf-idf
    vectorizer=TfidfVectorizer(stop_words='english')
    tfidf_matrix=vectorizer.fit_transform(text)
    
    # Reduce dimentionality using LSA (Latent Semantic Analysis)
    lsa=TruncatedSVD(n_components=100) # Reduce to 100 dimensions
    lsa_matrix=lsa.fit_transform(tfidf_matrix)
    
    # Compute cosine similarity between resume and job description
    resume_vector=lsa_matrix[0] # first row corresponds to the resume
    job_vectors=lsa_matrix[1:] # Remaining rows correspond to job_descriptions
    
    similarities=cosine_similarity([resume_vector], job_vectors)[0]
    
    # Sort job listings based on similarity scores
    ranked_jobs=sorted(zip(job_listings, similarities), key=lambda x: x[1], reverse=True)
    
    # Return job listings sorted by relevance 
    sorted_job_listings=[job[0] for job in ranked_jobs] # Extract sorted job dictionaries
    
    return sorted_job_listings