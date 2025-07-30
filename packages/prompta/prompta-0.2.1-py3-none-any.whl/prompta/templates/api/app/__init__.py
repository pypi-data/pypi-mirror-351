"""Minimal Prompta API template package."""

from fastapi import FastAPI

# The actual FastAPI application is created in ``main.py`` to make it easy for
# tools like ``uvicorn`` to locate it via the *module:variable* notation,
# e.g. ``uvicorn app.main:app``.

__all__ = ["FastAPI"]
