import os
import base64
import requests
from fastapi import FastAPI, File, UploadFile, Request, Body
from fastapi.responses import PlainTextResponse, JSONResponse
from typing import Union

app = FastAPI(title="OCR Proxy API")

# RunPod Configuration
RUNPOD_ENDPOINT_ID = "01s4u2uzv9343o"
RUNPOD_API_URL_SYNC = f"https://api.runpod.ai/v2/{RUNPOD_ENDPOINT_ID}/runsync"
RUNPOD_API_URL_ASYNC = f"https://api.runpod.ai/v2/{RUNPOD_ENDPOINT_ID}/run"
RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
if not RUNPOD_API_KEY:
    raise ValueError("RUNPOD_API_KEY environment variable is required")

async def process_pdf_bytes(pdf_bytes: bytes):
    """Process PDF bytes using RunPod synchronous endpoint (works well if RunPod completes in <60s)"""
    # Convert to base64
    pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
    
    # Call RunPod OCR endpoint synchronously
    # Since RunPod completes in ~20 seconds, this is well within Vercel's 60s timeout
    response = requests.post(
        RUNPOD_API_URL_SYNC,
        headers={
            'Authorization': f'Bearer {RUNPOD_API_KEY}',
            'Content-Type': 'application/json'
        },
        json={
            "input": {
                "pdf_data": pdf_base64
            }
        },
        timeout=55  # Leave 5s buffer for Vercel 60s timeout
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
    Accepts PDF binary upload via form-data (recommended) OR raw binary body, converts to base64, calls RunPod OCR, returns OCR text
    """
    try:
        content_type = request.headers.get("content-type", "").lower()
        
        # Handle multipart/form-data (Postman "form-data" mode) - CHECK THIS FIRST
        if "multipart/form-data" in content_type:
            try:
                form = await request.form()
                
                # Debug: log all form keys
                form_keys = list(form.keys())
                
                file = form.get("file")
                
                if not file:
                    return JSONResponse(
                        status_code=400,
                        content={
                            "error": "No file provided in form-data. Use 'file' as the field name.",
                            "debug": {
                                "content_type": content_type,
                                "form_keys": form_keys,
                                "received_keys": [k for k in form_keys]
                            }
                        }
                    )
                
                # Validate file type
                if not file.filename or not file.filename.endswith('.pdf'):
                    return JSONResponse(
                        status_code=400,
                        content={"error": "Only PDF files are supported"}
                    )
                
                pdf_bytes = await file.read()
                
                if len(pdf_bytes) == 0:
                    return JSONResponse(
                        status_code=400,
                        content={"error": "File appears to be empty"}
                    )
                
                return await process_pdf_bytes(pdf_bytes)
            except Exception as e:
                return JSONResponse(
                    status_code=400,
                    content={"error": f"Error processing form-data: {str(e)}"}
                )
        
        # Handle raw binary upload (Postman "binary" mode)
        elif "application/pdf" in content_type or "application/octet-stream" in content_type:
            try:
                pdf_bytes = await request.body()
                
                # Check if we got valid bytes
                if not pdf_bytes or len(pdf_bytes) == 0:
                    return JSONResponse(
                        status_code=400,
                        content={"error": "Empty request body"}
                    )
                
                # Validate PDF magic bytes
                if not pdf_bytes.startswith(b'%PDF'):
                    return JSONResponse(
                        status_code=400,
                        content={"error": "Invalid PDF file. File must start with %PDF header."}
                    )
                
                return await process_pdf_bytes(pdf_bytes)
            except Exception as e:
                return JSONResponse(
                    status_code=400,
                    content={"error": f"Error reading binary data: {str(e)}"}
                )
        
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "error": f"Unsupported content-type: {content_type}. Use multipart/form-data (with 'file' field) or application/pdf for binary upload",
                    "received_content_type": request.headers.get("content-type", "none")
                }
            )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Server error: {str(e)}"}
        )

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "OCR Proxy API"}



