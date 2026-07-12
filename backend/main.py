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
from typing import List

# Vercel loads this file directly (not as the `backend` package), so relative
# imports (`from .calculator`) fail with ImportError and `app` is never defined
# -> "No FastAPI entrypoint found". Support both import styles.
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
except ImportError:  # running as a standalone module on Vercel
    from calculator import evaluate, available_functions, available_constants
    from models import (
        CalculateRequest,
        CalculateResponse,
        FunctionsResponse,
        ConstantsResponse,
        HealthResponse,
        FunctionInfo,
    )

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware.
# Allow all origins so the frontend works both when opened from
# http://localhost (web mode) and from file:// (desktop/pywebview mode).
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
async def health():
    return HealthResponse(status="ok", service="calculator")


@app.post("/calculate", response_model=CalculateResponse)
async def calculate(req: CalculateRequest):
    try:
        result = evaluate(req.expression)
        return CalculateResponse(result=result, expression=req.expression)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/functions", response_model=FunctionsResponse)
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
async def list_constants():
    return ConstantsResponse(constants=available_constants())


# ---------------------------------------------------------------------------
# Serve the frontend (HTML/CSS/JS) from the same origin so the desktop window
# and browser can load it directly at "/" and call the API without CORS issues.
# API routes above are matched first; anything else is served as a static file.
# ---------------------------------------------------------------------------
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
    # When running locally, default to 8000; on Vercel, use PORT env var
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)