"""Vercel entrypoint for the FastAPI app.

Vercel's Python runtime looks for a variable named ``app`` that is a
FastAPI instance. This wrapper simply re‑exports the ``app`` created in
``backend/main.py``.
"""

from backend.main import app  # noqa: F401  (re‑exported name)
