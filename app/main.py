from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import ingest, chat


app = FastAPI(
    title="Dr. Wilmer Gálvez Chatbot API",
    description="API del chatbot agente para el Dr. Wilmer Gálvez, candidato a la Alcaldía de El Alto 2026",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ingest.router, tags=["Ingestion"])
app.include_router(chat.router, tags=["Chat"])
app.include_router(chat.router, tags=["Chat"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "Dr. Wilmer Gálvez Chatbot API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {
        "status": "healthy",
        "service": "chatbot-api"
    }
