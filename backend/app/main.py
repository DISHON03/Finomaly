import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.app.config import settings
from backend.app.database import engine, Base, SessionLocal
from backend.app.models import *  # Ensure all models are registered
from backend.app.services.seed_service import seed_demo_data_if_needed

from backend.app.routers import (
    auth,
    transactions,
    budgets,
    savings,
    anomalies,
    forecasting,
    recurring,
    insights,
    categorization,
    tableau,
    dashboard
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure tables exist and seed demo account
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_demo_data_if_needed(db)
    except Exception as e:
        print(f"Warning during startup seed: {e}")
    finally:
        db.close()
    yield

app = FastAPI(
    title="Finomaly — Intelligent Expense Analytics & Anomaly Detection",
    version=settings.VERSION,
    description="Finomaly — Production-Grade AI-Powered Personal Finance Analytics System API. Understand Your Spending. Detect the Unusual.",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits local frontend vite dev server and production clients
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)
app.include_router(transactions.router, prefix=settings.API_V1_STR)
app.include_router(budgets.router, prefix=settings.API_V1_STR)
app.include_router(savings.router, prefix=settings.API_V1_STR)
app.include_router(anomalies.router, prefix=settings.API_V1_STR)
app.include_router(forecasting.router, prefix=settings.API_V1_STR)
app.include_router(recurring.router, prefix=settings.API_V1_STR)
app.include_router(insights.router, prefix=settings.API_V1_STR)
app.include_router(categorization.router, prefix=settings.API_V1_STR)
app.include_router(tableau.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "app": "Finomaly",
        "status": "operational",
        "version": settings.VERSION,
        "docs": "/docs",
        "api_v1": settings.API_V1_STR
    }

@app.get("/health")
def healthcheck():
    return {"status": "healthy"}
