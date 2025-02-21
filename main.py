from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel
import os
from langchain_nomic import NomicEmbeddings
from langchain_milvus import Milvus
from langchain_groq import ChatGroq
from upload import upload
from search import search
from store_update_delete import store, update, delete

load_dotenv()

app = FastAPI(debug=True)
print("App Initialized")

 
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Allow your React app’s origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (POST, GET, etc.)
    allow_headers=["*"],  # Allow all headers
)
 

# Load API keys
NOMIC_API_KEY = os.getenv("NOMIC_API_KEY")
MILVUS_API_KEY = os.getenv("MILVUS_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MILVUS_URI = os.getenv("MILVUS_URI")


 
# Initialize embeddings
embeddings = NomicEmbeddings(model="nomic-embed-text-v1", dimensionality=768, nomic_api_key=NOMIC_API_KEY)
print("Embeddings Created")

# Initialize vector store
index_params = {
    "metric_type": "IP",
    "index_type": "HNSW",
    "params": {"M": 8, "efConstruction": 10},
}
 
vector_store = Milvus(
    collection_name="resumes1",
    embedding_function=embeddings,
    connection_args={
        "uri": MILVUS_URI,
        "token": MILVUS_API_KEY
    },
    vector_field="content_dense",
    consistency_level="Strong",
    auto_id=False,
    primary_field="ids",
    index_params=index_params,
    enable_dynamic_field = True
)
print("Milvus collection initialized")
 
# Initialize LLM
llm = ChatGroq(model="llama3-70b-8192", temperature=0.3)
print("LLM Initialized")


class ResumeData(BaseModel):
    json_data: dict
    QR: int

class UpdateRequest(BaseModel):
    ids: list[str]
    updated_data: dict
    QR: int

class DeleteRequest(BaseModel):
    ids: list[str]

@app.post("/upload")                 # Parsing Resume
async def upload_resume(file: UploadFile = File(...)):
    """Accepts a PDF file from the frontend and passes it to the upload function."""
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    file_location = f"temp_{file.filename}"
    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())
    
    try:
        print("Uploading function called")
        uploaded_json = upload(file_location, llm, GROQ_API_KEY)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    finally:  
        os.remove(file_location)  # Cleanup tahe temporary file
    
    return {"json_data" : uploaded_json}




@app.post("/store")  
def calling_store(resume_data: ResumeData):                 # Need json_data and QR
    """Accepts JSON format data and stores it."""
    try:
        print("In calling store")
        uuids = store(resume_data.json_data, vector_store, resume_data.QR)  # Pass JSON data to store function
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error storing data: {str(e)}")
    return {"ids": uuids}



@app.get("/search")
def calling_search(query: str = Query(..., title="Search Query")):          # QR, Name, Score, Fields, Resumelink
    """Receives a search query from React.js and returns search results."""
    try:
        results = search(query, llm, vector_store, GROQ_API_KEY)  # Pass the query to the search function
        return {"candidates": results}  # Return the search results in JSON format
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching: {str(e)}")
    


@app.post("/update")
def calling_update(update_request: UpdateRequest):
    try:
        print("In calling update")
        updated_ids = update(update_request.ids, update_request.updated_data, vector_store, update_request.QR)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating data: {str(e)}")
    return {"updated_ids": updated_ids}


@app.post("/delete")
def calling_update(delete_request: DeleteRequest):
    try:
        print("In calling Delete")
        updated_ids = delete(delete_request.ids, vector_store)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Deleting data: {str(e)}")
    return {"Deleted_ids": updated_ids}