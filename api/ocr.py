import os
import base64
import requests
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import PlainTextResponse, JSONResponse

app = FastAPI(title="OCR Proxy API")

# RunPod Configuration
RUNPOD_API_URL = "https://api.runpod.ai/v2/01s4u2uzv9343o/runsync"
RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
if not RUNPOD_API_KEY:
    raise ValueError("RUNPOD_API_KEY environment variable is required")

@app.post("/ocr")
async def ocr_pdf(file: UploadFile = File(...)):
    """
    OCR Proxy Endpoint
    Accepts PDF binary upload, converts to base64, calls RunPod OCR, returns OCR text
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            return JSONResponse(
                status_code=400,
                content={"error": "Only PDF files are supported"}
            )
        
        # Read PDF binary
        pdf_bytes = await file.read()
        
        # Convert to base64
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # Call RunPod OCR endpoint
        response = requests.post(
            RUNPOD_API_URL,
            headers={
                'Authorization': f'Bearer {RUNPOD_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                "input": {
                    "pdf_data": pdf_base64
                }
            },
            timeout=120  # 2 minute timeout for OCR processing
        )
        
        if not response.ok:
            return JSONResponse(
                status_code=response.status_code,
                content={"error": f"RunPod API error: {response.text}"}
            )
        
        # Parse RunPod response
        result = response.json()
        ocr_data = result.get('output', result)
        
        if not ocr_data or not ocr_data.get('success'):
            return JSONResponse(
                status_code=500,
                content={"error": ocr_data.get('error', 'OCR processing failed')}
            )
        
        # Return OCR text as plain text
        ocr_text = ocr_data.get('ocr_text', '')
        return PlainTextResponse(content=ocr_text)
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "OCR Proxy API"}

