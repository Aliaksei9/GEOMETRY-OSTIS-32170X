#!/usr/bin/env python3
"""
API server using FastAPI that generates geometry tests using Grock LLM
"Receives POST requests with {"message": "user input"}, processes with Groq LLM"
Run with: uvicorn this_file:app --reload
Requires: pip install fastapi uvicorn groq
"""
from .test_generator import TestGenerator
from .key_manager import get_api_key
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).parent / ".env")


# --- FastAPI приложение ---
app = FastAPI()

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TestRequest(BaseModel):
    topic: str
    num_questions: int

@app.post("/generate-test")
async def generate_test_endpoint(req: TestRequest):
    api_key = get_api_key()
    if not api_key:
        raise HTTPException(status_code=500, detail="API key not found")
    
    generator = TestGenerator(api_key)
    test = generator.generate_test(req.topic, req.num_questions)
    
    if test:
        return test.to_dict()
    else:
        raise HTTPException(status_code=500, detail="Failed to generate test")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)