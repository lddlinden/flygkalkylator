from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from paddleocr import PaddleOCR
import io
from PIL import Image

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ocr = PaddleOCR(use_angle_cls=True, lang='en')

@app.post("/ocr")
async def perform_ocr(file: UploadFile = File(...)):
    image_data = await file.read()
    
    # PaddleOCR usually expects a file path or numpy array, 
    # but it can work with file-like objects if we save it to a temporary path 
    # or use the path directly if we save the upload.
    # Given the existing structure, let's save the file temporarily.
    
    with open("temp_image.jpg", "wb") as f:
        f.write(image_data)
        
    results = ocr.ocr("temp_image.jpg", cls=True)
    
    texts = []
    for line in results:
        for word in line:
            texts.append(word[1][0])
            
    text = " ".join(texts)
    
    return {"text": text}
