"""Restaurant service layer with business logic."""
from typing import Union, List, Dict, Any
import re
from datetime import datetime
from fastapi import HTTPException
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
    CostEstimateResponse,
    CreateReceiptRequest,
    ReceiptResponse,
    ReceiptItemDetail
)


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


def generate_receipt_id() -> str:
    """
    Generate a unique receipt ID.
    
    Returns:
        Receipt ID in format RCP-YYYYMMDD-XXX
    """
    date_str = datetime.utcnow().strftime("%Y%m%d")
    
    # Get count of receipts for today to generate sequence number
    receipts_col = db_service.get_receipts_collection()
    today_receipts = receipts_col.count_documents({
        "receipt_id": {"$regex": f"^RCP-{date_str}-"}
    })
    
    sequence = str(today_receipts + 1).zfill(3)
    return f"RCP-{date_str}-{sequence}"


def list_restaurants(limit: int = 100, skip: int = 0) -> Dict[str, Any]:
    """
    List all restaurants with pagination.
    
    Args:
        limit: Maximum number of restaurants to return
        skip: Number of restaurants to skip
        
    Returns:
        Dictionary with restaurants list and pagination info
    """
    restaurants_data = db_service.list_restaurants(limit=limit, skip=skip)
    total_count = db_service.get_restaurants_collection().count_documents({})
    
    restaurants = []
    for restaurant in restaurants_data:
        # Ensure _id is always present and valid
        if '_id' not in restaurant or restaurant.get('_id') is None:
            # Skip restaurants without _id (shouldn't happen, but handle gracefully)
            continue
        try:
            # Create Pydantic model instance
            restaurant_obj = RestaurantResponse(**restaurant)
            # Convert to dict using by_alias=False to ensure _id is included
            restaurant_dict = restaurant_obj.dict(by_alias=False)
            # Explicitly ensure _id is included and is a string
            restaurant_dict['_id'] = str(restaurant.get('_id'))
            restaurants.append(restaurant_dict)
        except Exception as e:
            # Skip restaurants that fail validation, but log the error
            import sys
            print(f"Warning: Failed to create RestaurantResponse for restaurant {restaurant.get('name', 'unknown')}: {e}", file=sys.stderr)
            continue
    
    return {
        "restaurants": restaurants,
        "total": total_count,
        "limit": limit,
        "skip": skip
    }


def get_restaurant_menu(restaurant_id: str) -> Dict[str, Any]:
    """
    Get menu items for a specific restaurant.
    
    Args:
        restaurant_id: MongoDB _id of the restaurant
        
    Returns:
        Dictionary with menu items
        
    Raises:
        HTTPException: If restaurant not found
    """
    # Get restaurant to verify it exists and get name
    restaurant = db_service.get_restaurant_by_id(restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    # Get menu items
    items_data = db_service.get_menu_items(restaurant_id)
    items = [MenuItemResponse(**item) for item in items_data]
    
    return {
        "restaurant_id": restaurant_id,
        "restaurant_name": restaurant.get('name'),
        "items": [item.dict() for item in items],
        "total_items": len(items)
    }


def get_restaurant_menu_by_name(restaurant_name: str) -> Dict[str, Any]:
    """
    Get menu items for a restaurant by name (case-insensitive).
    
    Args:
        restaurant_name: Name of the restaurant
        
    Returns:
        Dictionary with menu items
        
    Raises:
        HTTPException: If restaurant not found
    """
    # Get restaurant by name
    restaurant = db_service.get_restaurant_by_name(restaurant_name)
    if not restaurant:
        raise HTTPException(status_code=404, detail=f"Restaurant '{restaurant_name}' not found")
    
    restaurant_id = str(restaurant['_id'])
    
    # Get menu items
    items_data = db_service.get_menu_items(restaurant_id)
    items = [MenuItemResponse(**item) for item in items_data]
    
    return {
        "restaurant_id": restaurant_id,
        "restaurant_name": restaurant.get('name'),
        "items": [item.dict() for item in items],
        "total_items": len(items)
    }


def get_menu_item(item_id: str) -> Dict[str, Any]:
    """
    Get a single menu item by its ID.
    
    Args:
        item_id: MongoDB _id of the menu item
        
    Returns:
        Dictionary with menu item details
        
    Raises:
        HTTPException: If item not found
    """
    item_data = db_service.get_item_by_id(item_id)
    if not item_data:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item = MenuItemResponse(**item_data)
    return item.dict()


def build_cart(request: BuildCartRequest) -> Dict[str, Any]:
    """
    Build a shopping cart with items from a restaurant.
    
    Args:
        request: Cart request with restaurant_id and items
        
    Returns:
        Dictionary with cart details and totals
        
    Raises:
        HTTPException: If restaurant or items not found
    """
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
    
    cart = CartResponse(
        restaurant_id=request.restaurant_id,
        restaurant_name=restaurant.get('name'),
        items=cart_items,
        subtotal=round(subtotal, 2),
        delivery_fee=round(delivery_fee, 2) if delivery_fee else None,
        total=round(total, 2)
    )
    
    return cart.dict()


def compute_cost_estimate(request: CostEstimateRequest) -> Dict[str, Any]:
    """
    Compute cost estimate for a cart without building the full cart.
    
    Args:
        request: Cost estimate request with restaurant_id and items
        
    Returns:
        Dictionary with cost estimate
        
    Raises:
        HTTPException: If restaurant or items not found
    """
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
    
    estimate = CostEstimateResponse(
        restaurant_id=request.restaurant_id,
        restaurant_name=restaurant.get('name'),
        subtotal=round(subtotal, 2),
        delivery_fee=round(delivery_fee, 2) if delivery_fee else None,
        estimated_total=round(estimated_total, 2),
        estimated_tax=round(estimated_tax, 2)
    )
    
    return estimate.dict()


def create_receipt(request: CreateReceiptRequest) -> Dict[str, Any]:
    """
    Create a receipt for an order.
    
    Args:
        request: Receipt creation request with restaurant, items, and customer info
        
    Returns:
        Dictionary with receipt details
        
    Raises:
        HTTPException: If restaurant or items not found
    """
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
    
    # Build receipt items with details and calculate subtotal
    receipt_items = []
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
        
        receipt_items.append(ReceiptItemDetail(
            item_id=cart_item.item_id,
            name=item_data.get('name'),
            description=item_data.get('description'),
            price=item_price,
            quantity=cart_item.quantity,
            subtotal=item_subtotal
        ))
    
    # Get delivery fee from restaurant and parse it
    delivery_fee = parse_delivery_fee(restaurant.get('delivery_fee'))
    
    # Calculate tax (assuming 8.5% tax rate, can be made configurable)
    tax_rate = 0.085
    tax = subtotal * tax_rate
    
    # Calculate total
    total = subtotal + delivery_fee + tax
    
    # Generate receipt ID
    receipt_id = generate_receipt_id()
    
    # Create receipt document
    receipt_data = {
        "receipt_id": receipt_id,
        "restaurant_id": request.restaurant_id,
        "restaurant_name": restaurant.get('name'),
        "items": [item.dict() for item in receipt_items],
        "subtotal": round(subtotal, 2),
        "delivery_fee": round(delivery_fee, 2) if delivery_fee else None,
        "tax": round(tax, 2),
        "total": round(total, 2),
        "delivery_id": request.delivery_id,
        "customer_name": request.customer_name,
        "customer_email": request.customer_email,
        "customer_phone": request.customer_phone,
        "delivery_address": request.delivery_address,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    
    # Save receipt to database
    receipt_mongo_id = db_service.create_receipt(receipt_data)
    
    # Build response
    receipt = ReceiptResponse(
        _id=receipt_mongo_id,
        receipt_id=receipt_id,
        restaurant_id=request.restaurant_id,
        restaurant_name=restaurant.get('name'),
        items=receipt_items,
        subtotal=round(subtotal, 2),
        delivery_fee=round(delivery_fee, 2) if delivery_fee else None,
        tax=round(tax, 2),
        total=round(total, 2),
        delivery_id=request.delivery_id,
        customer_name=request.customer_name,
        customer_email=request.customer_email,
        customer_phone=request.customer_phone,
        delivery_address=request.delivery_address,
        created_at=receipt_data["created_at"]
    )
    
    return receipt.dict()

