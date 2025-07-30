#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bexy API - REST API for Python code execution in sandbox

This module provides a FastAPI server for executing Python code in a sandbox environment.
"""

import os
import sys
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from bexy.python_sandbox import PythonSandbox
from bexy.dependency_manager import DependencyManager
from bexy.docker_sandbox import DockerSandbox

# Create FastAPI app
app = FastAPI(
    title="Bexy API",
    description="""
    # Bexy API
    
    API for executing Python code in secure sandbox environments.
    
    ## Features
    
    * Execute Python code in isolated sandboxes
    * Support for both process-level and Docker-based isolation
    * Manage dependencies for code execution
    * Analyze Python code for imports and dependencies
    * Health check endpoint for monitoring
    """,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Models for request/response
class CodeExecutionRequest(BaseModel):
    code: str
    timeout: int = 10
    use_docker: bool = False

class DependencyRequest(BaseModel):
    package_name: str
    version: Optional[str] = None

class CodeAnalysisRequest(BaseModel):
    code: str

# API endpoints
@app.post("/execute", tags=["code"], response_model=Dict[str, Any])
async def execute_code(request: CodeExecutionRequest):
    """
    Execute Python code in a sandbox environment
    
    This endpoint allows you to run Python code in a secure sandbox. You can choose
    between a process-level sandbox or a Docker-based sandbox for stronger isolation.
    
    Example request:
    ```json
    {
        "code": "print('Hello, World!')",
        "timeout": 10,
        "use_docker": false
    }
    ```
    
    Example response:
    ```json
    {
        "success": true,
        "stdout": "Hello, World!\n",
        "stderr": "",
        "error_type": null,
        "error_message": null,
        "error": null
    }
    ```
    """
    try:
        if request.use_docker:
            # Use Docker sandbox for isolation
            sandbox = DockerSandbox()
            result = sandbox.run_code(request.code, timeout=request.timeout)
        else:
            # Use Python sandbox
            sandbox = PythonSandbox()
            result = sandbox.run_code(request.code, timeout=request.timeout)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/dependencies/install", tags=["dependencies"], response_model=Dict[str, Any])
async def install_dependency(request: DependencyRequest):
    """
    Install a Python package in the sandbox environment
    
    This endpoint allows you to install Python packages for use in the sandbox environment.
    You can specify a version or let the system use the latest available version.
    
    Example request:
    ```json
    {
        "package_name": "requests",
        "version": "2.28.1"
    }
    ```
    
    Example response:
    ```json
    {
        "success": true,
        "message": "Successfully installed requests 2.28.1"
    }
    ```
    """
    try:
        manager = DependencyManager()
        success, message = manager.install_package(request.package_name, request.version)
        if not success:
            raise HTTPException(status_code=400, detail=message)
        return {"success": True, "message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze", tags=["code"], response_model=Dict[str, Any])
async def analyze_code(request: CodeAnalysisRequest):
    """
    Analyze Python code for imports and dependencies
    
    This endpoint analyzes Python code to identify imports, dependencies, and potential issues.
    
    Example request:
    ```json
    {
        "code": "import requests\n\nresponse = requests.get('https://example.com')\nprint(response.text)"
    }
    ```
    
    Example response:
    ```json
    {
        "imports": ["requests"],
        "external_dependencies": ["requests"],
        "standard_library_imports": [],
        "potential_issues": []
    }
    ```
    """
    try:
        from bexy.code_analyzer import CodeAnalyzer
        analyzer = CodeAnalyzer()
        analysis = analyzer.analyze_code(request.code)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health", tags=["system"], response_model=Dict[str, str])
async def health_check():
    """
    Check if the API is running
    
    This endpoint provides a simple health check to verify that the API is operational.
    It can be used by monitoring systems to check the service status.
    
    Example response:
    ```json
    {
        "status": "healthy",
        "version": "0.1.0",
        "service": "Bexy API"
    }
    ```
    """
    return {
        "status": "healthy",
        "version": "0.1.0",
        "service": "Bexy API"
    }

def start_server(host="0.0.0.0", port=8000):
    """Start the Bexy API server"""
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start_server()
