import os
import base64
import requests
import time
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
    """Process PDF bytes using RunPod async endpoint with polling to avoid Vercel timeout"""
    # Convert to base64
    pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
    
    # Start async job
    response = requests.post(
        RUNPOD_API_URL_ASYNC,
        headers={
            'Authorization': f'Bearer {RUNPOD_API_KEY}',
            'Content-Type': 'application/json'
        },
        json={
            "input": {
                "pdf_data": pdf_base64
            }
        },
        timeout=10  # Quick timeout for job submission
    )
    
    if not response.ok:
        return JSONResponse(
            status_code=response.status_code,
            content={"error": f"RunPod API error: {response.text}"}
        )
    
    job_data = response.json()
    job_id = job_data.get('id')
    
    if not job_id:
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to start RunPod job"}
        )
    
    # Poll for results - leave 10s buffer for Vercel 60s timeout
    max_wait = 50  # seconds
    start_time = time.time()
    poll_interval = 1  # Poll every 1 second
    
    while time.time() - start_time < max_wait:
        status_response = requests.get(
            f"https://api.runpod.ai/v2/{RUNPOD_ENDPOINT_ID}/status/{job_id}",
            headers={
                'Authorization': f'Bearer {RUNPOD_API_KEY}'
            },
            timeout=5
        )
        
        if status_response.ok:
            status_data = status_response.json()
            status = status_data.get('status')
            
            if status == 'COMPLETED':
                output = status_data.get('output', {})
                
                # Handle different response formats
                if isinstance(output, dict):
                    ocr_data = output.get('output', output)
                    
                    if isinstance(ocr_data, dict):
                        if not ocr_data.get('success'):
                            return JSONResponse(
                                status_code=500,
                                content={"error": ocr_data.get('error', 'OCR processing failed')}
                            )
                        ocr_text = ocr_data.get('ocr_text', '')
                    else:
                        ocr_text = str(ocr_data)
                else:
                    ocr_text = str(output)
                
                return PlainTextResponse(content=ocr_text)
            
            elif status == 'FAILED':
                error_msg = status_data.get('error', 'RunPod job failed')
                return JSONResponse(
                    status_code=500,
                    content={"error": f"RunPod job failed: {error_msg}"}
                )
            
            # Status is IN_PROGRESS or QUEUED, continue polling
            time.sleep(poll_interval)
        else:
            # If status check fails, wait a bit and retry
            time.sleep(poll_interval)
    
    # Timeout - return job ID for client to poll
    return JSONResponse(
        status_code=202,
        content={
            "message": "OCR processing started but not completed within timeout. Poll for results.",
            "job_id": job_id,
            "status_url": f"https://api.runpod.ai/v2/{RUNPOD_ENDPOINT_ID}/status/{job_id}",
            "poll_instructions": "Use GET request to status_url with Authorization header to check job status"
        }
    )

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


