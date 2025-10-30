# OCR Proxy API - Testing Guide

## Quick Start

### Option 1: Test Locally (Recommended First)

1. **Install dependencies:**
```bash
cd contract-parser-api
pip install -r requirements.txt
```

2. **Set environment variable:**
```bash
export RUNPOD_API_KEY="your_runpod_api_key_here"
```

3. **Start the server:**
```bash
uvicorn api.ocr:app --reload --port 8000
```

4. **Test with curl:**
```bash
# Health check
curl http://localhost:8000/health

# OCR test (replace path with your PDF)
curl -X POST http://localhost:8000/ocr \
  -F "file=@Tenancy_Contract.pdf"
```

### Option 2: Use Test Script

```bash
# Install requests if not already installed
pip install requests

# Set API key
export RUNPOD_API_KEY="your_runpod_api_key_here"

# Run tests
python test_api.py Tenancy_Contract.pdf
```

### Option 3: Deploy to Vercel and Test

1. **Deploy to Vercel:**
```bash
# Install Vercel CLI if needed
npm i -g vercel

# Deploy
cd contract-parser-api
vercel --prod
```

2. **Set environment variable in Vercel:**
   - Go to Vercel Dashboard → Your Project → Settings → Environment Variables
   - Add: `RUNPOD_API_KEY` = `your_runpod_api_key_here`

3. **Test deployed endpoint:**
```bash
# Replace with your Vercel URL
curl -X POST https://your-app.vercel.app/ocr \
  -F "file=@Tenancy_Contract.pdf"
```

## Test Endpoints

### Health Check
```bash
GET /health
```

### OCR Endpoint
```bash
POST /ocr
Content-Type: multipart/form-data
Body: file=<PDF binary>
```

**Response:**
- Success: Plain text OCR output
- Error: `{"error": "error message"}`

## Expected Response

Success:
```
[Plain text OCR output from RunPod]
```

Error:
```json
{
  "error": "Only PDF files are supported"
}
```

## Troubleshooting

**"RUNPOD_API_KEY environment variable is required"**
- Make sure you've set the environment variable before starting the server

**"Connection refused"**
- Make sure uvicorn server is running on port 8000

**"Timeout"**
- OCR processing can take 30-60+ seconds for large PDFs
- Vercel Hobby plan has 10s timeout (will fail)
- Vercel Pro plan has 60s timeout (should work)

**"File not found"**
- Make sure the PDF file path is correct
- Use absolute path if relative path doesn't work



## Quick Start

### Option 1: Test Locally (Recommended First)

1. **Install dependencies:**
```bash
cd contract-parser-api
pip install -r requirements.txt
```

2. **Set environment variable:**
```bash
export RUNPOD_API_KEY="your_runpod_api_key_here"
```

3. **Start the server:**
```bash
uvicorn api.ocr:app --reload --port 8000
```

4. **Test with curl:**
```bash
# Health check
curl http://localhost:8000/health

# OCR test (replace path with your PDF)
curl -X POST http://localhost:8000/ocr \
  -F "file=@Tenancy_Contract.pdf"
```

### Option 2: Use Test Script

```bash
# Install requests if not already installed
pip install requests

# Set API key
export RUNPOD_API_KEY="your_runpod_api_key_here"

# Run tests
python test_api.py Tenancy_Contract.pdf
```

### Option 3: Deploy to Vercel and Test

1. **Deploy to Vercel:**
```bash
# Install Vercel CLI if needed
npm i -g vercel

# Deploy
cd contract-parser-api
vercel --prod
```

2. **Set environment variable in Vercel:**
   - Go to Vercel Dashboard → Your Project → Settings → Environment Variables
   - Add: `RUNPOD_API_KEY` = `your_runpod_api_key_here`

3. **Test deployed endpoint:**
```bash
# Replace with your Vercel URL
curl -X POST https://your-app.vercel.app/ocr \
  -F "file=@Tenancy_Contract.pdf"
```

## Test Endpoints

### Health Check
```bash
GET /health
```

### OCR Endpoint
```bash
POST /ocr
Content-Type: multipart/form-data
Body: file=<PDF binary>
```

**Response:**
- Success: Plain text OCR output
- Error: `{"error": "error message"}`

## Expected Response

Success:
```
[Plain text OCR output from RunPod]
```

Error:
```json
{
  "error": "Only PDF files are supported"
}
```

## Troubleshooting

**"RUNPOD_API_KEY environment variable is required"**
- Make sure you've set the environment variable before starting the server

**"Connection refused"**
- Make sure uvicorn server is running on port 8000

**"Timeout"**
- OCR processing can take 30-60+ seconds for large PDFs
- Vercel Hobby plan has 10s timeout (will fail)
- Vercel Pro plan has 60s timeout (should work)

**"File not found"**
- Make sure the PDF file path is correct
- Use absolute path if relative path doesn't work

