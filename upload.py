import os
import json
from dotenv import load_dotenv
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_nomic import NomicEmbeddings
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core import ChatPromptTemplate
from llama_index.llms.groq import Groq
from datetime import datetime
load_dotenv()

default_dict = {
            "Name": "",
            "Contact": {
                "Email": "",
                "Phone_no": "",
                "Address": "",
                "LinkedIn": "",
                "GitHub": "",
                "Twitter": ""
            },
            "Domain": "",
            "Personal_Projects": [
                {
                    "Project_Title": "",
                    "Project_Description": "",
                    "TechStack": [],
                    "Start_date": "",
                    "End_date": ""
                }
            ],
            "Experience": [
                {
                    "Project_Title": "",
                    "Company": "",
                    "Location": "",
                    "Start_date": "",
                    "End_date": "",
                    "Description": "",
                    "TechStack": [],
                    "Client": "",
                    "Role": "",
                    "Responsibilities": [],
                }
            ],
            "Highest_Qualification": {
                "Degree": "",
                "Institution": "",
                "Score": ""
            },
            "Skills": [],
            "Certifications": [
                {
                    "Name": "",
                    "Title": "",
                    "Certified_Date": "",
                    "Validity_Date": "",
                    "Provider": ""
                }
            ],
            "Awards_and_Recognitions": [],
            "Research_and_Publications": [
                {
                    "Title": "",
                    "Description": "",
                    "year": ""
                }
            ],
            "Other_Details": [{}]
        }


def get_resume_text(file_path):
    loader = PDFPlumberLoader(file_path=file_path)
    raw_documents = loader.load()
    return "".join(doc.page_content for doc in raw_documents)

def create_prompt(data):
    prompt = f"""
        Create a Json format for the below resume details:
        details: {data}
    """
    chat_text_qa_msgs = [
        ChatMessage(
            role=MessageRole.SYSTEM,
            content=f"""
                You are a text resume parser. Extract the details from the resume and present them in the following format.
                Format: {default_dict}
                If there are any additional details in the resume that don't fit into the main categories, put them under "other details."
                If any fields are missing in the provided format, fill them with empty random text relevant to the key.
                If there are no explicit skills listed in the resume, extract the skills from the projects section.
                In that the date formate should be dd-mm-YYYY, If any date or month missing in the formate place the random number that should not change the existing date details.
                Strictly restricted to respond with only JSON format in response and nothing more extra context.
            """
        ),
        ChatMessage(role=MessageRole.USER, content=prompt),
    ]
    text_qa_template = ChatPromptTemplate(chat_text_qa_msgs)
    original_prompt = text_qa_template.format_messages(chat_text_qa_msgs)
    return original_prompt

def parse_resume(resume_text, llm, GROQ_API_KEY):
    prompt = create_prompt(resume_text)
    llm = Groq(model="llama3-70b-8192", temperature=0.1, api_key = GROQ_API_KEY)
    response = llm.chat(prompt)
    response_text = response.message.blocks[0].text.strip()
    if "```" in response_text:
        response_text = response_text.split("```")[1]

    return json.loads(response_text)


def upload(file, llm, GROQ_API_KEY):
    resume_text = get_resume_text(file)                      # Get the text formate of Resume
    parsed_resume = parse_resume(resume_text, llm, GROQ_API_KEY)
    return parsed_resume
