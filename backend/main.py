from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import easyocr
import io
import requests
from datetime import datetime, timedelta
from PIL import Image

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

reader = easyocr.Reader(['en'], gpu=False)

def get_nautical_twilight(date: str):
    # Växjö coordinates
    lat = 56.8777
    lng = 14.8091
    url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lng}&date={date}&formatted=0"
    response = requests.get(url)
    data = response.json()
    if data['status'] == 'OK':
        results = data['results']
        # Convert UTC to local time (approximate CET/CEST - simplified)
        # Note: A real implementation would handle timezones properly
        nautical_twilight_begin = datetime.fromisoformat(results['nautical_twilight_begin'].replace('Z', '+00:00'))
        nautical_twilight_end = datetime.fromisoformat(results['nautical_twilight_end'].replace('Z', '+00:00'))
        return nautical_twilight_begin.time(), nautical_twilight_end.time()
    return None, None

@app.get("/twilight")
async def get_twilight(date: str):
    begin, end = get_nautical_twilight(date)
    return {"begin": str(begin) if begin else None, "end": str(end) if end else None}

@app.post("/ocr")
async def perform_ocr(file: UploadFile = File(...)):
    image_data = await file.read()
    
    image = Image.open(io.BytesIO(image_data))
    results = reader.readtext(image, detail=0)
    text = " ".join(results)
    
    return {"text": text}
