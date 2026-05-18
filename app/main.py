from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import orders, webhooks, admin, products, analytics
import logging
import time
import asyncio
from contextlib import asynccontextmanager
from app.core.cron import reconcile_pending_orders

# Configure logging to write to a file
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start the background cron job
    task = asyncio.create_task(reconcile_pending_orders())
    yield
    # Shutdown: Cancel the task
    task.cancel()

# FastAPI automatically generates beautiful, interactive API documentation
# using Swagger UI. We can access it at the /docs endpoint.
app = FastAPI(
    title="Hunkx Apparel API",
    description="Layer 2 Backend Engine. Features automated Swagger UI documentation, strict data validation, and Razorpay integration.",
    version="1.0.0",
    docs_url="/docs",     # Access Swagger UI here
    redoc_url="/redoc",   # Access alternative ReDoc UI here
    lifespan=lifespan
)

import os

# CORS configuration to allow our Next.js frontend to talk to this backend
# We use wildcard "*" to completely eliminate CORS issues. 
# Security is handled via our Bearer tokens (Supabase Auth), not cookies, so allow_credentials=False is safe and correct.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(
        f"Method: {request.method} Path: {request.url.path} "
        f"Status: {response.status_code} Time: {process_time:.4f}s"
    )
    return response

# Include our API routes cleanly
app.include_router(orders.router, prefix="/api/v1")
app.include_router(webhooks.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {
        "status": "success", 
        "message": "Hunkx Backend Layer 2 is online. Visit http://127.0.0.1:8000/docs for Swagger API documentation."
    }
