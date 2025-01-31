from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import Optional
import asyncio
from pathlib import Path
import tempfile
import os

from codegen.dependency_inliner import DependencyInliner

app = FastAPI()

# Initialize the dependency inliner
inliner = DependencyInliner()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze_code(file: UploadFile):
    if not file.filename.endswith('.py'):
        raise HTTPException(status_code=400, detail="Only Python files are supported")
    
    # Create a temporary file to store the uploaded content
    with tempfile.NamedTemporaryFile(delete=False, suffix='.py') as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_path = temp_file.name

    try:
        # Run the analysis and code generation asynchronously
        # For now, we'll pass an empty dependency map since we're just inlining the code
        result = await asyncio.get_event_loop().run_in_executor(
            None, 
            inliner.inline_dependencies,
            temp_path,
            {}  # Empty dependency map for now
        )
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up the temporary file
        os.unlink(temp_path)

@app.post("/submit-code")
async def submit_code(code: dict):
    try:
        # Create a temporary file with the submitted code
        with tempfile.NamedTemporaryFile(delete=False, suffix='.py') as temp_file:
            temp_file.write(code["content"].encode())
            temp_path = temp_file.name

        try:
            # Run the analysis and code generation asynchronously
            result = await asyncio.get_event_loop().run_in_executor(
                None, 
                inliner.inline_dependencies,
                temp_path,
                {}  # Empty dependency map for now
            )
            return {"result": result}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            # Clean up the temporary file
            os.unlink(temp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
