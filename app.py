"""
Main FastAPI application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.restaurants import router as restaurants_router
from routers.doordash import router as doordash_router
from routers.agent import router as agent_router

app = FastAPI(
    title="DaNomNoms API",
    description="REST API for DaNomNoms food delivery service",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(restaurants_router)
app.include_router(doordash_router)
app.include_router(agent_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to DaNomNoms API",
        "version": "1.0.0",
        "endpoints": {
            "list_restaurants": "GET /api/restaurants/",
            "get_menu": "GET /api/restaurants/{restaurant_id}/menu",
            "get_item": "GET /api/restaurants/items/{item_id}",
            "build_cart": "POST /api/restaurants/cart",
            "compute_cost_estimate": "POST /api/restaurants/cost-estimate",
            "create_receipt": "POST /api/restaurants/receipts",
            "create_delivery": "POST /api/doordash/deliveries",
            "track_delivery": "GET /api/doordash/deliveries/{external_delivery_id}",
            "agent_chat": "POST /api/agent/chat"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

