from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import orders

# FastAPI automatically generates beautiful, interactive API documentation
# using Swagger UI. We can access it at the /docs endpoint.
app = FastAPI(
    title="Hunkx Apparel API",
    description="Layer 2 Backend Engine. Features automated Swagger UI documentation, strict data validation, and Razorpay integration.",
    version="1.0.0",
    docs_url="/docs",     # Access Swagger UI here
    redoc_url="/redoc",   # Access alternative ReDoc UI here
)

# CORS configuration to allow our Next.js frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include our API routes cleanly
app.include_router(orders.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "status": "success", 
        "message": "Hunkx Backend Layer 2 is online. Visit http://127.0.0.1:8000/docs for Swagger API documentation."
    }
