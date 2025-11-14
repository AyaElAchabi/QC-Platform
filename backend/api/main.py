"""
Point d entree principal de l application FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import auth, projects, images, annotations, labelstudio, dataset_import, training
from core.database import engine, Base

# Creer les tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MLOps QC Platform API",
    description="API pour la plateforme de controle qualite visuel",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router, tags=["auth"])
app.include_router(projects.router, tags=["projects"])
app.include_router(images.router, tags=["images"])
app.include_router(annotations.router, tags=["annotations"])
app.include_router(labelstudio.router, tags=["labelstudio"])
app.include_router(dataset_import.router, tags=["dataset"])
app.include_router(training.router, tags=["training"])

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0"
    }
