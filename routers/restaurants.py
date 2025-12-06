"""
Restaurant-related API endpoints.
"""
from typing import Optional, Union
import re
from fastapi import APIRouter, HTTPException, Query
from database import db_service
from models import (
    ListRestaurantsResponse,
    RestaurantResponse,
    MenuResponse,
    MenuItemResponse,
    BuildCartRequest,
    CartResponse,
    CartItemDetail,
    CostEstimateRequest,
    CostEstimateResponse
)

router = APIRouter(prefix="/api/restaurants", tags=["restaurants"])


def parse_delivery_fee(value: Union[float, str, None]) -> float:
    """
    Parse delivery fee from various formats.
    
    Args:
        value: Delivery fee as float, string, or None
        
    Returns:
        Parsed delivery fee as float, or 0.0 if None/unparseable
    """
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        # Try to extract number from strings like "$0 delivery fee, first order" or "$2.99"
        match = re.search(r'\$?(\d+\.?\d*)', value)
        if match:
            return float(match.group(1))
        return 0.0
    return 0.0


def parse_price(value: Union[float, str, None]) -> float:
    """
    Parse price from various formats.
    
    Args:
        value: Price as float, string, or None
        
    Returns:
        Parsed price as float, or 0.0 if None/unparseable
    """
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        # Try to extract number from strings like "$$16.99" or "$12.99" or "16.99"
        match = re.search(r'(\d+\.?\d*)', value)
        if match:
            return float(match.group(1))
        return 0.0
    return 0.0


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
        restaurants_data = db_service.list_restaurants(limit=limit, skip=skip)
        total_count = db_service.get_restaurants_collection().count_documents({})
        
        restaurants = [RestaurantResponse(**restaurant) for restaurant in restaurants_data]
        
        return ListRestaurantsResponse(
            restaurants=restaurants,
            total=total_count,
            limit=limit,
            skip=skip
        )
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
        # Get restaurant to verify it exists and get name
        restaurant = db_service.get_restaurant_by_id(restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        # Get menu items
        items_data = db_service.get_menu_items(restaurant_id)
        items = [MenuItemResponse(**item) for item in items_data]
        
        return MenuResponse(
            restaurant_id=restaurant_id,
            restaurant_name=restaurant.get('name'),
            items=items,
            total_items=len(items)
        )
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
        item_data = db_service.get_item_by_id(item_id)
        if not item_data:
            raise HTTPException(status_code=404, detail="Item not found")
        
        return MenuItemResponse(**item_data)
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
        # Verify restaurant exists
        restaurant = db_service.get_restaurant_by_id(request.restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        # Get all item IDs from the cart
        item_ids = [item.item_id for item in request.items]
        
        # Fetch item details from database
        items_data = db_service.get_items_by_ids(item_ids)
        
        if len(items_data) != len(item_ids):
            raise HTTPException(
                status_code=400,
                detail="One or more items not found or invalid"
            )
        
        # Create a mapping of item_id to item data
        items_map = {item['_id']: item for item in items_data}
        
        # Build cart items with details
        cart_items = []
        subtotal = 0.0
        
        for cart_item in request.items:
            item_data = items_map.get(cart_item.item_id)
            if not item_data:
                raise HTTPException(
                    status_code=400,
                    detail=f"Item {cart_item.item_id} not found"
                )
            
            item_price = parse_price(item_data.get('price'))
            item_subtotal = item_price * cart_item.quantity
            subtotal += item_subtotal
            
            cart_items.append(CartItemDetail(
                item_id=cart_item.item_id,
                name=item_data.get('name'),
                description=item_data.get('description'),
                price=item_price,
                quantity=cart_item.quantity,
                subtotal=item_subtotal
            ))
        
        # Get delivery fee from restaurant and parse it
        delivery_fee = parse_delivery_fee(restaurant.get('delivery_fee'))
        
        total = subtotal + delivery_fee
        
        return CartResponse(
            restaurant_id=request.restaurant_id,
            restaurant_name=restaurant.get('name'),
            items=cart_items,
            subtotal=round(subtotal, 2),
            delivery_fee=round(delivery_fee, 2) if delivery_fee else None,
            total=round(total, 2)
        )
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
        # Verify restaurant exists
        restaurant = db_service.get_restaurant_by_id(request.restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        # Get all item IDs from the request
        item_ids = [item.item_id for item in request.items]
        
        # Fetch item details from database
        items_data = db_service.get_items_by_ids(item_ids)
        
        if len(items_data) != len(item_ids):
            raise HTTPException(
                status_code=400,
                detail="One or more items not found or invalid"
            )
        
        # Create a mapping of item_id to item data
        items_map = {item['_id']: item for item in items_data}
        
        # Calculate subtotal
        subtotal = 0.0
        for cart_item in request.items:
            item_data = items_map.get(cart_item.item_id)
            if not item_data:
                raise HTTPException(
                    status_code=400,
                    detail=f"Item {cart_item.item_id} not found"
                )
            
            item_price = parse_price(item_data.get('price'))
            subtotal += item_price * cart_item.quantity
        
        # Get delivery fee from restaurant and parse it
        delivery_fee = parse_delivery_fee(restaurant.get('delivery_fee'))
        
        # Calculate estimated tax (assuming 8.5% tax rate, can be made configurable)
        tax_rate = 0.085
        estimated_tax = subtotal * tax_rate
        
        # Calculate total
        estimated_total = subtotal + delivery_fee + estimated_tax
        
        return CostEstimateResponse(
            restaurant_id=request.restaurant_id,
            restaurant_name=restaurant.get('name'),
            subtotal=round(subtotal, 2),
            delivery_fee=round(delivery_fee, 2) if delivery_fee else None,
            estimated_total=round(estimated_total, 2),
            estimated_tax=round(estimated_tax, 2)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error computing cost estimate: {str(e)}")
