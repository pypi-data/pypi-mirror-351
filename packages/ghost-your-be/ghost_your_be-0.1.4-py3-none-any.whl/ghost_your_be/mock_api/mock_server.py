from fastapi import FastAPI, HTTPException, Query
from .api_generator import APIGenerator
import uvicorn
import os
from typing import Optional

app = FastAPI(
    title="Ghost Your BE Mock API",
    description="Mock API server for frontend development",
    version="1.0.0"
)

@app.get("/mock/{endpoint}")
async def mock_endpoint(
    endpoint: str,
    count: int = Query(default=5, ge=1, le=1000, description="Number of records to generate"),
    code: int = Query(default=200, description="HTTP status code to return"),
    message: str = Query(default="Success", description="Response message")
):
    """
    Generate mock data for the specified endpoint.
    
    Args:
        endpoint: The endpoint name (corresponds to table name in schema)
        count: Number of records to generate (1-1000)
        code: HTTP status code to return
        message: Response message
        
    Returns:
        JSON response with generated data
    """
    schema_path = os.environ.get("SCHEMA_PATH")
    if not schema_path:
        raise HTTPException(
            status_code=500,
            detail="SCHEMA_PATH environment variable is not set"
        )
    
    try:
        generator = APIGenerator(schema_path)
        response = generator.generate_response(
            endpoint=endpoint,
            count=count,
            code=code,
            message=message
        )
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating mock data: {str(e)}")

def run_mock_server(host="0.0.0.0", port=8000):
    """Run the mock API server."""
    uvicorn.run(app, host=host, port=port)