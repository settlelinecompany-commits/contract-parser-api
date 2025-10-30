# Contract Parser OCR API

Simple FastAPI proxy that accepts PDF uploads, converts to base64, calls RunPod OCR endpoint, and returns OCR text.

## API Endpoints

### POST `/ocr`
Accepts PDF file upload and returns OCR text.

**Request:**
```bash
curl -X POST https://your-vercel-url.vercel.app/ocr \
  -F "file=@contract.pdf"
```

**Response:**
- Success: Plain text OCR output
- Error: `{"error": "error message"}`

### GET `/health`
Health check endpoint.

## Environment Variables

**Required** - Set in Vercel dashboard:
- `RUNPOD_API_KEY` - RunPod API key (required)

## Deployment

Deploy to Vercel:
```bash
vercel --prod
```

## Requirements

- Python 3.x
- FastAPI
- requests
- python-multipart

See `requirements.txt` for exact versions.


Simple FastAPI proxy that accepts PDF uploads, converts to base64, calls RunPod OCR endpoint, and returns OCR text.

## API Endpoints

### POST `/ocr`
Accepts PDF file upload and returns OCR text.

**Request:**
```bash
curl -X POST https://your-vercel-url.vercel.app/ocr \
  -F "file=@contract.pdf"
```

**Response:**
- Success: Plain text OCR output
- Error: `{"error": "error message"}`

### GET `/health`
Health check endpoint.

## Environment Variables

**Required** - Set in Vercel dashboard:
- `RUNPOD_API_KEY` - RunPod API key (required)

## Deployment

Deploy to Vercel:
```bash
vercel --prod
```

## Requirements

- Python 3.x
- FastAPI
- requests
- python-multipart

See `requirements.txt` for exact versions.

