from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.utils.config import settings
from app.routers import health, chat

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    # Set all CORS enabled origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # For internship project, allowing all. Update for production.
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include Routers
    app.include_router(health.router, prefix=settings.API_V1_STR, tags=["health"])
    app.include_router(chat.router, prefix=settings.API_V1_STR, tags=["chat"])

    return app

app = create_app()

@app.get("/")
def root():
    return {"message": "Welcome to the AI Customer Support Agent API"}
