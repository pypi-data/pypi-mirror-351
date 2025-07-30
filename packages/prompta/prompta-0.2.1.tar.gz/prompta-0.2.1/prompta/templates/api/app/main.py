"""Very small FastAPI application shipped with the Prompta CLI.

The generated project is meant to be a starting point – users will typically
extend it or replace it entirely.  For that reason we keep the code minimal:

* A single health-check endpoint so that the CLI can verify the server is up.
* CORS middleware with permissive defaults for local development.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Prompta API", version="0.1.0")

# Allow everything during development – tighten this in production!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
    """Return a simple *OK* payload so clients can probe the service."""

    return {"status": "ok"}


@app.get("/")
async def root() -> dict[str, str]:
    """Welcome message – mainly so the index is not empty."""

    return {
        "message": "Welcome to the Prompta API prototype!",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
