import os
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware 
load_dotenv()

app = FastAPI()

origins = [
    "http://localhost:3000",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

API_URL = os.getenv("API_URL", "http://dummyurl.com")

@app.get("/")
async def root():
    return {"message": "SlideProf's server is working :D"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    files = {"file": (file.filename, file.file, file.content_type)}
    response = requests.post(f"{API_URL}/upload_pdf", files=files)
    return response.json()

@app.post("/ask")
async def ask_question(request: Request):
    data = await request.json()
    filename = data.get("filename")
    question = data.get("question")
    page_number = data.get("pageNumber")
    coordinates = data.get("imageCoords")
    
    if not filename or not question or page_number is None or not coordinates:
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    response = requests.post(f"{API_URL}/process_pdf/", data={
        "filename": filename,
        "page_number": page_number,
        "coordinates": ",".join(map(str, coordinates))
    })
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json().get("detail", "Error processing PDF"))
    
    return response.json()