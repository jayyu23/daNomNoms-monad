"""
Restaurant-related API endpoints.
"""
from fastapi import APIRouter, HTTPException, Query
from models import (
    ListRestaurantsResponse,
    MenuResponse,
    MenuItemResponse,
    BuildCartRequest,
    CartResponse,
    CostEstimateRequest,
    CostEstimateResponse,
    CreateReceiptRequest,
    ReceiptResponse
)
from services import restaurant_service

router = APIRouter(prefix="/api/restaurants", tags=["restaurants"])


@router.get("/", response_model=ListRestaurantsResponse)
async def list_restaurants(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of restaurants to return"),
    skip: int = Query(0, ge=0, description="Number of restaurants to skip")
):
    """
    List all restaurants with pagination.
    
    Returns a paginated list of all restaurants in the database.
    
    Example curl request:
    ```bash
    curl "http://localhost:8000/api/restaurants/?limit=10&skip=0"
    ```
    """
    try:
        result = restaurant_service.list_restaurants(limit=limit, skip=skip)
        return ListRestaurantsResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching restaurants: {str(e)}")


@router.get("/{restaurant_id}/menu", response_model=MenuResponse)
async def get_menu(restaurant_id: str):
    """
    Get menu items for a specific restaurant.
    
    Args:
        restaurant_id: MongoDB _id of the restaurant
        
    Returns:
        Menu items for the restaurant
    
    Example curl request:
    ```bash
    curl "http://localhost:8000/api/restaurants/69347db4fa0aa2fde8fdaeb3/menu"
    ```
    """
    try:
        result = restaurant_service.get_restaurant_menu(restaurant_id)
        return MenuResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching menu: {str(e)}")


@router.get("/items/{item_id}", response_model=MenuItemResponse)
async def get_item(item_id: str):
    """
    Get a single menu item by its ID.
    
    Args:
        item_id: MongoDB _id of the menu item
        
    Returns:
        Menu item details
    
    Example curl request:
    ```bash
    curl "http://localhost:8000/api/restaurants/items/69347db5fa0aa2fde8fdaf17"
    ```
    """
    try:
        result = restaurant_service.get_menu_item(item_id)
        return MenuItemResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching item: {str(e)}")


@router.post("/cart", response_model=CartResponse)
async def build_cart(request: BuildCartRequest):
    """
    Build a shopping cart with items from a restaurant.
    
    Args:
        request: Cart request with restaurant_id and items
        
    Returns:
        Cart with item details and totals
    
    Example curl request:
    ```bash
    curl -X POST http://localhost:8000/api/restaurants/cart \
      -H "Content-Type: application/json" \
      -d '{
        "restaurant_id": "69347db4fa0aa2fde8fdaeb3",
        "items": [
          {
            "item_id": "69347db5fa0aa2fde8fdaf17",
            "quantity": 2
          },
          {
            "item_id": "69347db5fa0aa2fde8fdaf18",
            "quantity": 1
          }
        ]
      }'
    ```
    """
    try:
        result = restaurant_service.build_cart(request)
        return CartResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error building cart: {str(e)}")


@router.post("/cost-estimate", response_model=CostEstimateResponse)
async def compute_cost_estimate(request: CostEstimateRequest):
    """
    Compute cost estimate for a cart without building the full cart.
    
    Args:
        request: Cost estimate request with restaurant_id and items
        
    Returns:
        Cost estimate with subtotal, delivery fee, and total
    
    Example curl request:
    ```bash
    curl -X POST http://localhost:8000/api/restaurants/cost-estimate \
      -H "Content-Type: application/json" \
      -d '{
        "restaurant_id": "69347db4fa0aa2fde8fdaeb6",
        "items": [
          {
            "item_id": "69347db5fa0aa2fde8fdafc4",
            "quantity": 2
          }
        ]
      }'
    ```
    """
    try:
        result = restaurant_service.compute_cost_estimate(request)
        return CostEstimateResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error computing cost estimate: {str(e)}")


@router.post("/receipts", response_model=ReceiptResponse)
async def create_receipt(request: CreateReceiptRequest):
    """
    Create a receipt for an order.
    
    This endpoint creates a receipt record for a completed order, including
    all items, pricing, and customer information.
    
    Args:
        request: Receipt creation request with restaurant, items, and customer info
        
    Returns:
        Receipt response with receipt details and ID
    
    Example curl request:
    ```bash
    curl -X POST http://localhost:8000/api/restaurants/receipts \
      -H "Content-Type: application/json" \
      -d '{
        "restaurant_id": "69347db4fa0aa2fde8fdaeb3",
        "items": [
          {
            "item_id": "69347db5fa0aa2fde8fdaf17",
            "quantity": 2
          },
          {
            "item_id": "69347db5fa0aa2fde8fdaf18",
            "quantity": 1
          }
        ],
        "delivery_id": "D-12345",
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "customer_phone": "+16505555555",
        "delivery_address": "123 Main St, San Francisco, CA 94103"
      }'
    ```
    """
    try:
        result = restaurant_service.create_receipt(request)
        return ReceiptResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating receipt: {str(e)}")
