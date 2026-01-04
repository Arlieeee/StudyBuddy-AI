"""FastAPI main application entry point."""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import upload_router, qa_router, generate_router, recommendations_router

# Get settings
settings = get_settings()

# Ensure data directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.VECTORDB_DIR, exist_ok=True)

# Create FastAPI app
app = FastAPI(
    title="StudyBuddy AI",
    description="多模态智能学习助手 - 基于 Gemini 3 的 RAG 知识问答系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload_router)
app.include_router(qa_router)
app.include_router(generate_router)
app.include_router(recommendations_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "StudyBuddy AI",
        "version": "1.0.0",
        "description": "多模态智能学习助手",
        "endpoints": {
            "docs": "/docs",
            "upload": "/upload",
            "qa": "/qa",
            "generate": "/generate",
            "recommendations": "/recommendations",
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
