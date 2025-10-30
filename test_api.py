#!/usr/bin/env python3
"""
Test script for OCR Proxy API
Tests both local and deployed endpoints
"""

import os
import sys
import requests
from pathlib import Path

# Configuration
RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
if not RUNPOD_API_KEY:
    print("⚠️  RUNPOD_API_KEY environment variable is required")
    print("   Set it with: export RUNPOD_API_KEY=your_key")
    sys.exit(1)
LOCAL_URL = "http://localhost:8000"
VERCEL_URL = os.getenv("VERCEL_URL", "")  # Set this after deployment

def test_health(base_url: str):
    """Test health endpoint"""
    print(f"\n🔍 Testing health endpoint: {base_url}/health")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Response: {response.json()}")
        return response.ok
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_ocr(base_url: str, pdf_path: str):
    """Test OCR endpoint with PDF file"""
    print(f"\n📄 Testing OCR endpoint: {base_url}/ocr")
    print(f"📁 PDF file: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return False
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': (os.path.basename(pdf_path), f, 'application/pdf')}
            print(f"🚀 Sending request...")
            response = requests.post(
                f"{base_url}/ocr",
                files=files,
                timeout=180  # 3 minutes for OCR processing
            )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.ok:
            ocr_text = response.text
            print(f"✅ OCR Success!")
            print(f"📝 Text length: {len(ocr_text)} characters")
            print(f"📄 Preview (first 500 chars):\n{ocr_text[:500]}...")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 OCR Proxy API Test Suite")
    print("=" * 60)
    
    # Find test PDF
    test_pdf = None
    possible_paths = [
        "Tenancy_Contract.pdf",
        "tenancy_contract.pdf",
        "../contract-dashboard/Tenancy_Contract.pdf",
        "../Tenancy_Contract.pdf"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            test_pdf = path
            break
    
    if not test_pdf:
        print("\n⚠️  No test PDF found. Please provide PDF path as argument:")
        print("   python test_api.py <path_to_pdf>")
        print("\nOr place Tenancy_Contract.pdf in current directory")
        if len(sys.argv) > 1:
            test_pdf = sys.argv[1]
        else:
            return
    
    # Test mode
    mode = os.getenv("TEST_MODE", "local")
    
    if mode == "local":
        print("\n📍 Testing LOCAL server")
        print("   Make sure server is running: uvicorn api.ocr:app --reload")
        
        # Test health
        if not test_health(LOCAL_URL):
            print("\n❌ Local server not running. Start it with:")
            print("   cd contract-parser-api")
            print("   export RUNPOD_API_KEY=your_key")
            print("   uvicorn api.ocr:app --reload")
            return
        
        # Test OCR
        test_ocr(LOCAL_URL, test_pdf)
        
    elif mode == "vercel":
        if not VERCEL_URL:
            print("\n❌ VERCEL_URL not set. Set it with:")
            print("   export VERCEL_URL=https://your-app.vercel.app")
            return
        
        print(f"\n📍 Testing VERCEL deployment: {VERCEL_URL}")
        test_health(VERCEL_URL)
        test_ocr(VERCEL_URL, test_pdf)
    
    else:
        print(f"\n❌ Unknown TEST_MODE: {mode}")
        print("   Use: export TEST_MODE=local or export TEST_MODE=vercel")

if __name__ == "__main__":
    main()



