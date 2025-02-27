from langchain_core.documents import Document
from datetime import datetime
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
 
formatter = logging.Formatter('%(asctime)s:%(filename)s:%(funcName)s:%(levelname)s:%(message)s')
 
file_Handler = logging.FileHandler('main_log.log')
file_Handler.setLevel(logging.INFO)
file_Handler.setFormatter(formatter)
 
stream_Handler = logging.StreamHandler()
stream_Handler.setFormatter(formatter)
 
 
logger.addHandler(file_Handler)
logger.addHandler(stream_Handler)
 

# Descriptions
def get_personal_project_description(personal_project):
    return f"""Worked on the {personal_project["Project_Title"]} project from {personal_project["Start_date"]} to {personal_project["End_date"]}. This project focused on {personal_project["Project_Description"]} and utilized technologies such as {', '.join(personal_project["TechStack"])} to achieve its objectives."""
 
 
def get_experience_description(company_project):
    return f"""Worked on the {company_project["Project_Title"]} project at {company_project["Company"]} in {company_project["Location"]} from {company_project["Start_date"]} to {company_project["End_date"]}. The project utilized technologies such as {', '.join(company_project["TechStack"]) if len(company_project["TechStack"])>0 else company_project["TechStack"]}, and was developed for the client {company_project["Client"]}. In my role as a {company_project["Role"]}, I was responsible for {', '.join(company_project["Responsibilities"]) if len(company_project["Responsibilities"])>0 else company_project["Responsibilities"]}."""
 
 
def get_certifications_description(certification):
    return f""" Certified by {certification["Provider"]} with the title of {certification["Title"]} was issued on {certification["Certified_Date"]} and valid up to {certification["Validity_Date"] if certification["Validity_Date"]!="" else datetime.now().year}."""
 
def get_skills_description(skills):
    return f"""Developed strong skills in {', '.join(skills)} contributing to professional growth and effectiveness."""
 
def get_publications_description(publications):
    return f""" Published research title{publications["Title"]} on {publications["year"]}, focusing on {publications["Description"]}, contributing to advancements in the field."""
 
 
def get_recognitions_decription(recognitions):
    return f"""Received the {', '.join(recognitions) if len(recognitions)>1 else recognitions}, award in recognition of outstanding achievements and contributions"""
   

# Get Date difference
def get_dates_difference(date1, date2):
    start_date = datetime.strptime(str(date1), "%Y-%m-%d")  
    end_date = datetime.strptime(str(date2), "%Y-%m-%d")    
    difference = (end_date - start_date).days
    return difference/365

 
# Get Documents
def get_doc_experience(json_data, index):
    content = get_experience_description(json_data['Experience'][index])
    return Document(
        metadata={
            "source": f"{json_data['Name']}_resume.pdf",
            "Candidate_Name": f"{json_data['Name']}",
            "Email": f"{json_data['Contact']['Email']}",
            "Domain": f"{json_data['Domain']}",
            "type": "Experience",
            "Project_Title": f"{json_data['Experience'][index]['Project_Title']}",
            "Description": content
        },
        page_content=content
    )
 
 
def get_doc_project(json_data, index):
    content = get_personal_project_description(json_data['Personal_Projects'][index])
    return Document(
        metadata={
            "source": f"{json_data['Name']}_resume.pdf",
            "Candidate_Name": f"{json_data['Name']}",
            "Email": f"{json_data['Contact']['Email']}",
            "Domain": f"{json_data['Domain']}",
            "type": "Projects",
            "Project_Title": f"{json_data['Personal_Projects'][index]['Project_Title']}",
            "Description": content
        },
        page_content=content
    )
 
def get_doc_certifications(json_data, index):
    content = get_certifications_description(json_data['Certifications'][index])
    return Document(
        metadata={
            "source": f"{json_data['Name']}_resume.pdf",
            "Candidate_Name": f"{json_data['Name']}",
            "Email": f"{json_data['Contact']['Email']}",
            "Domain": f"{json_data['Domain']}",
            "type": "Certifications",
            "Project_Title": "",
            # "Certification_Name": f"{json_data["Certifications"][index]["Title"]}",
            "Description": content
        },
        page_content=content
    )
 
 
def get_doc_skills(json_data):
    content = get_skills_description(json_data["Skills"])
    return Document(
        metadata={
            "source": f"{json_data['Name']}_resume.pdf",
            "Candidate_Name": f"{json_data['Name']}",
            "Email": f"{json_data['Contact']['Email']}",
            "Domain": f"{json_data['Domain']}",
            "type": "Skills",
            "Project_Title": "",
            "Description": content
        },
        page_content=content
    )
 
 
def get_doc_publications(json_data, index):
    content = get_publications_description(json_data["Research_and_Publications"][index])
    return Document(
        metadata={
            "source": f"{json_data['Name']}_resume.pdf",
            "Candidate_Name": f"{json_data['Name']}",
            "Email": f"{json_data['Contact']['Email']}",
            "Domain": f"{json_data['Domain']}",
            "type": "Research_and_Publications",
            "Project_Title": f"{json_data['Research_and_Publications'][index]['Title']}",
            "Description": content
        },
        page_content=content
    )
 
def get_doc_recognitions(json_data):
    content = get_recognitions_decription(json_data["Awards_and_Recognitions"])
    return Document(
        metadata={
            "source": f"{json_data['Name']}_resume.pdf",
            "Candidate_Name": f"{json_data['Name']}",
            "Email": f"{json_data['Contact']['Email']}",
            "Domain": f"{json_data['Domain']}",
            "type": "Awards_and_Recognitions",
            "Project_Title": "",
            "Description": content
        },
        page_content=content
    )


# Documents Declaration
def get_documents(json_data, QR):
    current_date = datetime.now()
    resume_chunking_documents = []
    no_of_records = 0
    total_experience = 0
 
    logger.info("Personal Project...")
    if len(json_data["Personal_Projects"])>=1:
        logger.info("Inside loop")
        for exp_index in range(len(json_data["Personal_Projects"])):
            resume_chunking_documents.append(get_doc_project(json_data, exp_index))
            no_of_records += 1
 
    logger.info("Experience...")
    if len(json_data["Experience"]):
        for exp_index in range(len(json_data["Experience"])):
            resume_chunking_documents.append(get_doc_experience(json_data, exp_index))
            if json_data["Experience"][exp_index]["End_date"].lower() == "current" or json_data["Experience"][exp_index]["End_date"].lower() == "present":
                json_data["Experience"][exp_index]["End_date"] = current_date.date()
            total_experience += get_dates_difference(json_data["Experience"][exp_index]["Start_date"] ,json_data["Experience"][exp_index]["End_date"])
            no_of_records += 1
 
    logger.info("Certifications...")
    if len(json_data["Certifications"]):
        for exp_index in range(len(json_data["Certifications"])):
            resume_chunking_documents.append(get_doc_certifications(json_data, exp_index))
            no_of_records += 1
 
    logger.info("Skills...")
    if len(json_data["Skills"]):
        resume_chunking_documents.append(get_doc_skills(json_data))
        no_of_records += 1
 
    logger.info("Awards and Recognitions...")
    if len(json_data["Awards_and_Recognitions"]):
        resume_chunking_documents.append(get_doc_recognitions(json_data))
        no_of_records += 1
 
    logger.info("Reasearch and Publications...")
    if len(json_data["Research_and_Publications"]):
        for exp_index in range(len(json_data["Research_and_Publications"])):
            resume_chunking_documents.append(get_doc_publications(json_data, exp_index))
            no_of_records += 1

    documents = resume_chunking_documents
    uuids = [str(uuid4()) for _ in range(len(documents))]

    for i in range(len(documents)):
        documents[i].metadata["QR"] = QR
        documents[i].metadata["Total_experience"] = round(total_experience,2)
        documents[i].metadata["No_of_Records"] = no_of_records
    logger.info("Document are ready to return")
    return (documents, uuids)
   
 

def store(json_data, vector_store, QR):
    logger.info("In Store")
    logger.info(json_data)
    documents, uuids = get_documents(json_data, QR)
    logger.info(f"{len(documents)} documents are getting to store")
    vector_store.add_documents(documents=documents, ids = uuids)
    logger.info("Successfully Stored")
    return uuids



def update(ids, json_data, vector_store, QR):
    vector_store.delete(ids=ids)
    return store(json_data, vector_store, QR)


def delete(ids, vector_store):
    logger.info("In Delete")
    vector_store.delete(ids=ids)
    logger.info("Successfully Deleted")
    return ids