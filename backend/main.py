"""FastAPI application for the calculator service.

Endpoints:
- POST /calculate: evaluate an expression
- GET /functions: list available functions
- GET /constants: list available constants
- GET /health: health check
"""

import os
import uvicorn
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List

# Local imports – Vercel runs the file as a module, so relative imports must work both ways
try:
    from .calculator import evaluate, available_functions, available_constants
    from .models import (
        CalculateRequest,
        CalculateResponse,
        FunctionsResponse,
        ConstantsResponse,
        HealthResponse,
        FunctionInfo,
    )
except ImportError:  # When executed as a script (e.g., uvicorn backend.main:app)
    from calculator import evaluate, available_functions, available_constants
    from models import (
        CalculateRequest,
        CalculateResponse,
        FunctionsResponse,
        ConstantsResponse,
        HealthResponse,
        FunctionInfo,
    )

app = FastAPI()

# CORS – allow the frontend (served from Vercel) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.title = "Calculator Service"
app.version = "1.0.0"

@app.get("/health")
@app.get("/api/health")
async def health():
    return HealthResponse(status="ok", service="calculator")

@app.post("/calculate", response_model=CalculateResponse)
@app.post("/api/calculate", response_model=CalculateResponse)
async def calculate(req: CalculateRequest):
    try:
        result = evaluate(req.expression)
        return CalculateResponse(result=result, expression=req.expression)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/functions", response_model=FunctionsResponse)
@app.get("/api/functions", response_model=FunctionsResponse)
async def list_functions():
    func_list = [
        FunctionInfo(
            name=name,
            arity=2 if name == "pow" else 1,
            description="Available function",
        )
        for name in available_functions()
    ]
    return FunctionsResponse(functions=func_list)

@app.get("/constants", response_model=ConstantsResponse)
@app.get("/api/constants", response_model=ConstantsResponse)
async def list_constants():
    return ConstantsResponse(constants=available_constants())

# Serve the frontend from the root path when deployed on Vercel
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND_DIR.exists():
    @app.get("/")
    async def index():
        return FileResponse(str(FRONTEND_DIR / "index.html"))

    app.mount(
        "/",
        StaticFiles(directory=str(FRONTEND_DIR), html=True),
        name="frontend",
    )

if __name__ == "__main__":
    # Vercel sets PORT in the environment; default to 8000 for local dev
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
