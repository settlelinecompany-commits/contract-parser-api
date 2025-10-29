import os
import base64
import requests
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import PlainTextResponse, JSONResponse

app = FastAPI(title="OCR Proxy API")

# RunPod Configuration
RUNPOD_API_URL = "https://api.runpod.ai/v2/01s4u2uzv9343o/runsync"
RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
if not RUNPOD_API_KEY:
    raise ValueError("RUNPOD_API_KEY environment variable is required")

async def process_pdf_bytes(pdf_bytes: bytes):
    """Common function to process PDF bytes and call RunPod"""
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

@app.post("/ocr")
async def ocr_pdf(request: Request):
    """
    OCR Proxy Endpoint
    Accepts PDF binary upload via form-data OR raw binary body, converts to base64, calls RunPod OCR, returns OCR text
    """
    try:
        content_type = request.headers.get("content-type", "")
        
        # Handle raw binary upload (Postman "binary" mode)
        if "application/pdf" in content_type or "application/octet-stream" in content_type or not content_type:
            pdf_bytes = await request.body()
            
            # Validate PDF magic bytes
            if not pdf_bytes.startswith(b'%PDF'):
                return JSONResponse(
                    status_code=400,
                    content={"error": "Invalid PDF file. File must start with %PDF header."}
                )
            
            return await process_pdf_bytes(pdf_bytes)
        
        # Handle multipart/form-data (Postman "form-data" mode)
        elif "multipart/form-data" in content_type:
            form = await request.form()
            file = form.get("file")
            
            if not file:
                return JSONResponse(
                    status_code=400,
                    content={"error": "No file provided in form-data"}
                )
            
            # Validate file type
            if not file.filename or not file.filename.endswith('.pdf'):
                return JSONResponse(
                    status_code=400,
                    content={"error": "Only PDF files are supported"}
                )
            
            pdf_bytes = await file.read()
            return await process_pdf_bytes(pdf_bytes)
        
        else:
            return JSONResponse(
                status_code=400,
                content={"error": f"Unsupported content-type: {content_type}. Use multipart/form-data or application/pdf"}
            )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "OCR Proxy API"}

