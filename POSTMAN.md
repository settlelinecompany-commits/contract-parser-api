# Postman Test Instructions

## Setup

### 1. Request Configuration
- **Method:** `POST`
- **URL:** `http://localhost:8000/ocr` (local) or `https://your-app.vercel.app/ocr` (Vercel)

### 2. Headers
No headers needed - Postman will set `Content-Type: multipart/form-data` automatically

### 3. Body
- **Option 1: form-data (RECOMMENDED & WORKS)**
  - **Type:** `form-data`
  - **Key:** `file` (dropdown must say "File")
  - **Value:** Click "Select Files" and choose your PDF
  
- **Option 2: binary (REQUIRES HEADER)**
  - **Type:** `binary`
  - **Value:** Click "Select Files" and choose your PDF
  - **IMPORTANT:** Go to Headers tab and ADD:
    - **Key:** `Content-Type`
    - **Value:** `application/pdf`
  - Without this header, FastAPI will reject the request with a validation error

### 4. Environment Variables (Optional)
Create a Postman environment:
- `base_url`: `http://localhost:8000` or `https://your-app.vercel.app`

Then use: `{{base_url}}/ocr`

## Quick Test Steps

1. **Open Postman**
2. **Create New Request**
   - Method: `POST`
   - URL: `http://localhost:8000/ocr`
3. **Go to Body tab**
   - Select `form-data`
   - Key: `file` (dropdown should say "File")
   - Value: Click "Select Files" and choose your PDF
4. **Send**

## Expected Response

**Success (200):**
```
[Plain text OCR output from PDF]
```

**Error (400/500):**
```json
{
  "error": "Only PDF files are supported"
}
```

## Health Check (Optional)

- **Method:** `GET`
- **URL:** `http://localhost:8000/health`
- **Response:** `{"status":"healthy","service":"OCR Proxy API"}`

