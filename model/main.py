from dotenv import load_dotenv
import os
from openai import OpenAI
from model import run_model, encode_image, run_speech_model
from utils import extract_image_from_pdf
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import shutil
from pathlib import Path

app = FastAPI()

origins = [
    "http://localhost:50000",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pdf_storage_path = Path("./uploaded_pdfs")

pdf_storage_path.mkdir(parents=True, exist_ok=True)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the PDF to Speech API"}

@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        file_location = pdf_storage_path / file.filename
        with open(file_location, "wb") as pdf_file:
            shutil.copyfileobj(file.file, pdf_file)
        
        return {"filename": file.filename, "message": "PDF uploaded successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while uploading the PDF: {str(e)}")

@app.post("/process_pdf")
async def process_pdf(
    filename: str = Form(...),   
    query: str = Form(...),     
    page_number: int = Form(...),     
    coordinates: str = Form(...)      
):
    try:
        pdf_path = pdf_storage_path / filename
        if not pdf_path.exists():
            raise HTTPException(status_code=404, detail="PDF file not found")
        coordinates_list = [float(x) for x in coordinates.split(",")]
        
        if len(coordinates_list) != 4:
            raise HTTPException(status_code=400, detail="Invalid coordinates, must be a list of 4 integers: [x, y, x1, y1]")
        
        x, y, x1, y1 = coordinates_list
        print(x,y,x1,y1)
        
        print("EXTRACTING")
        img = extract_image_from_pdf(str(pdf_path), page_number, (x, y, x1, y1))
        # img.show()
        print("DONE EXTRACTING")
        if img is None:
            raise HTTPException(status_code=400, detail="Could not extract image from PDF")
        
        base64_image = encode_image(img)
        response = run_model(client, query + f". COORDS: (x: {x}, y: {y}, a: {x1}, b: {y1})", base64_image)
        # if response[0] != "{":
        #     return {"message": """
        #         "type": "text",
        #         "steps": [
        #             {
        #                 "explanation": "I'm sorry, I couldn't find an answer to your question.",
        #                 "items": []
        #             }
        #         ],
        #         "audio": []
        #     """}
        encoded_speech_arrays = run_speech_model(client, response)
        print("End audio processing")
        return {"message": response, "audio": encoded_speech_arrays}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the PDF: {str(e)}")