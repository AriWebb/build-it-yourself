from fastapi import FastAPI, UploadFile, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import Optional, Dict
import asyncio
from pathlib import Path
import tempfile
import os
import json

from codegen.dependency_inliner import DependencyInliner
from depanalyzer.dependency_analyzer import DependencyAnalyzer

app = FastAPI()

# Initialize the dependency analyzer
analyzer = DependencyAnalyzer()

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

# Store active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    active_connections[client_id] = websocket
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        del active_connections[client_id]

async def send_progress_update(client_id: str, message: str):
    if client_id in active_connections:
        await active_connections[client_id].send_json({
            "type": "progress",
            "message": message
        })

@app.post("/analyze/{client_id}")
async def analyze_code(file: UploadFile, client_id: str):
    if not file.filename.endswith('.py'):
        raise HTTPException(status_code=400, detail="Only Python files are supported")
    
    # Create a temporary file to store the uploaded content
    with tempfile.NamedTemporaryFile(delete=False, suffix='.py') as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_path = temp_file.name

    try:
        # Send initial progress update
        await send_progress_update(client_id, "Starting code analysis...")
        
        # Send parsing progress update
        await send_progress_update(client_id, "Parsing code and fetching dependencies...")
        
        # Run the dependency analysis
        dependency_map = await asyncio.get_event_loop().run_in_executor(
            None, 
            analyzer.analyze_file,
            temp_path
        )
        
        # Send generation progress update
        await send_progress_update(client_id, "Generating code with dependency results...")
        
        # Run the code generation
        result = await asyncio.get_event_loop().run_in_executor(
            None, 
            inliner.inline_dependencies,
            temp_path,
            dependency_map  # Empty dependency map for now
        )
        
        # Send the complete code through WebSocket
        if client_id in active_connections:
            await active_connections[client_id].send_json({
                "type": "complete",
                "code": result
            })
        
        # Send completion update
        await send_progress_update(client_id, "Analysis complete!")
        
        return {"result": result}
    except Exception as e:
        await send_progress_update(client_id, f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up the temporary file
        os.unlink(temp_path)

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
