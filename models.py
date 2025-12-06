"""
Pydantic models for request and response schemas.
"""
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator
import re


class RestaurantResponse(BaseModel):
    """Restaurant response model."""
    _id: str
    store_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    delivery_fee: Optional[Union[float, str]] = None
    eta: Optional[Union[int, str]] = None
    average_rating: Optional[float] = None
    number_of_ratings: Optional[Union[int, str]] = None
    price_range: Optional[Union[str, int]] = None
    distance_miles: Optional[float] = None
    link: Optional[str] = None
    address: Optional[str] = None
    operating_hours: Optional[str] = None
    items: Optional[List[str]] = None
    
    @field_validator('delivery_fee', mode='before')
    @classmethod
    def parse_delivery_fee(cls, v):
        """Parse delivery fee from string or return as-is."""
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str):
            # Try to extract number from strings like "$0 delivery fee, first order" or "$2.99"
            match = re.search(r'\$?(\d+\.?\d*)', v)
            if match:
                return float(match.group(1))
            return v  # Return original string if can't parse
        return v
    
    @field_validator('eta', mode='before')
    @classmethod
    def parse_eta(cls, v):
        """Parse ETA from string or return as-is."""
        if v is None:
            return None
        if isinstance(v, int):
            return v
        if isinstance(v, str):
            # Try to extract minutes from strings like "3.1 mi • 36 min" or "36 min"
            match = re.search(r'(\d+)\s*min', v)
            if match:
                return int(match.group(1))
            return v  # Return original string if can't parse
        return v
    
    @field_validator('number_of_ratings', mode='before')
    @classmethod
    def parse_number_of_ratings(cls, v):
        """Parse number of ratings from string or return as-is."""
        if v is None:
            return None
        if isinstance(v, int):
            return v
        if isinstance(v, str):
            # Try to parse strings like "(3k+)" or "100" or "1.2k"
            v_clean = v.strip('()')
            if 'k+' in v_clean.lower():
                match = re.search(r'(\d+\.?\d*)', v_clean)
                if match:
                    return int(float(match.group(1)) * 1000)
            # Try to extract just numbers
            match = re.search(r'(\d+)', v_clean)
            if match:
                return int(match.group(1))
            return v  # Return original string if can't parse
        return v
    
    @field_validator('price_range', mode='before')
    @classmethod
    def parse_price_range(cls, v):
        """Parse price range from int or string."""
        if v is None:
            return None
        if isinstance(v, int):
            # Convert int to dollar signs (1 -> "$", 2 -> "$$", etc.)
            return "$" * v
        return str(v)
    
    class Config:
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "store_id": "12345",
                "name": "Example Restaurant",
                "description": "A great place to eat",
                "delivery_fee": 2.99,
                "eta": 30,
                "average_rating": 4.5,
                "number_of_ratings": 100,
                "price_range": "$$",
                "distance_miles": 2.5,
                "address": "123 Main St",
                "operating_hours": "Mon-Sun: 10am-10pm"
            }
        }


class MenuItemResponse(BaseModel):
    """Menu item response model."""
    _id: str
    store_id: Optional[str] = None
    restaurant_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Union[float, str]] = None
    rating_percent: Optional[float] = None
    review_count: Optional[int] = None
    image_url: Optional[str] = None
    
    @field_validator('price', mode='before')
    @classmethod
    def parse_price(cls, v):
        """Parse price from string or return as-is."""
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str):
            # Try to extract number from strings like "$$16.99" or "$12.99" or "16.99"
            match = re.search(r'(\d+\.?\d*)', v)
            if match:
                return float(match.group(1))
            return v  # Return original string if can't parse
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439012",
                "store_id": "12345",
                "name": "Burger",
                "description": "Delicious burger",
                "price": 12.99,
                "rating_percent": 95.0,
                "review_count": 50,
                "image_url": "https://example.com/burger.jpg"
            }
        }


class CartItem(BaseModel):
    """Cart item model."""
    item_id: str = Field(..., description="MongoDB _id of the menu item")
    quantity: int = Field(..., ge=1, description="Quantity of the item")
    
    class Config:
        json_schema_extra = {
            "example": {
                "item_id": "507f1f77bcf86cd799439012",
                "quantity": 2
            }
        }


class BuildCartRequest(BaseModel):
    """Request model for building a cart."""
    restaurant_id: str = Field(..., description="MongoDB _id of the restaurant")
    items: List[CartItem] = Field(..., min_items=1, description="List of items to add to cart")
    
    class Config:
        json_schema_extra = {
            "example": {
                "restaurant_id": "507f1f77bcf86cd799439011",
                "items": [
                    {
                        "item_id": "507f1f77bcf86cd799439012",
                        "quantity": 2
                    },
                    {
                        "item_id": "507f1f77bcf86cd799439013",
                        "quantity": 1
                    }
                ]
            }
        }


class CartItemDetail(BaseModel):
    """Cart item with details."""
    item_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    quantity: int
    subtotal: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "item_id": "507f1f77bcf86cd799439012",
                "name": "Burger",
                "description": "Delicious burger",
                "price": 12.99,
                "quantity": 2,
                "subtotal": 25.98
            }
        }


class CartResponse(BaseModel):
    """Cart response model."""
    restaurant_id: str
    restaurant_name: Optional[str] = None
    items: List[CartItemDetail]
    subtotal: float
    delivery_fee: Optional[float] = None
    total: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "restaurant_id": "507f1f77bcf86cd799439011",
                "restaurant_name": "Example Restaurant",
                "items": [
                    {
                        "item_id": "507f1f77bcf86cd799439012",
                        "name": "Burger",
                        "price": 12.99,
                        "quantity": 2,
                        "subtotal": 25.98
                    }
                ],
                "subtotal": 25.98,
                "delivery_fee": 2.99,
                "total": 28.97
            }
        }


class CostEstimateRequest(BaseModel):
    """Request model for cost estimate."""
    restaurant_id: str = Field(..., description="MongoDB _id of the restaurant")
    items: List[CartItem] = Field(..., min_items=1, description="List of items in cart")
    
    class Config:
        json_schema_extra = {
            "example": {
                "restaurant_id": "507f1f77bcf86cd799439011",
                "items": [
                    {
                        "item_id": "507f1f77bcf86cd799439012",
                        "quantity": 2
                    }
                ]
            }
        }


class CostEstimateResponse(BaseModel):
    """Cost estimate response model."""
    restaurant_id: str
    restaurant_name: Optional[str] = None
    subtotal: float
    delivery_fee: Optional[float] = None
    estimated_total: float
    estimated_tax: Optional[float] = Field(None, description="Estimated tax (if applicable)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "restaurant_id": "507f1f77bcf86cd799439011",
                "restaurant_name": "Example Restaurant",
                "subtotal": 25.98,
                "delivery_fee": 2.99,
                "estimated_total": 28.97,
                "estimated_tax": 2.34
            }
        }


class ListRestaurantsResponse(BaseModel):
    """Response model for listing restaurants."""
    restaurants: List[RestaurantResponse]
    total: int
    limit: int
    skip: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "restaurants": [],
                "total": 100,
                "limit": 20,
                "skip": 0
            }
        }


class MenuResponse(BaseModel):
    """Response model for menu."""
    restaurant_id: str
    restaurant_name: Optional[str] = None
    items: List[MenuItemResponse]
    total_items: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "restaurant_id": "507f1f77bcf86cd799439011",
                "restaurant_name": "Example Restaurant",
                "items": [],
                "total_items": 50
            }
        }


class DoorDashCreateDeliveryRequest(BaseModel):
    """Request model for creating a DoorDash delivery."""
    external_delivery_id: str = Field(..., description="Unique identifier for the delivery")
    pickup_address: str = Field(..., description="Pickup address")
    pickup_business_name: str = Field(..., description="Business name for pickup location")
    pickup_phone_number: str = Field(..., description="Phone number for pickup location")
    pickup_instructions: Optional[str] = Field(None, description="Special instructions for pickup")
    pickup_reference_tag: Optional[str] = Field(None, description="Reference tag for pickup")
    dropoff_address: str = Field(..., description="Dropoff address")
    dropoff_business_name: Optional[str] = Field(None, description="Business name for dropoff location")
    dropoff_phone_number: str = Field(..., description="Phone number for dropoff location")
    dropoff_instructions: Optional[str] = Field(None, description="Special instructions for dropoff")
    dropoff_contact_given_name: Optional[str] = Field(None, description="Contact first name")
    dropoff_contact_family_name: Optional[str] = Field(None, description="Contact last name")
    order_value: Optional[int] = Field(None, description="Order value in cents")
    
    class Config:
        json_schema_extra = {
            "example": {
                "external_delivery_id": "D-12345",
                "pickup_address": "901 Market Street 6th Floor San Francisco, CA 94103",
                "pickup_business_name": "Wells Fargo SF Downtown",
                "pickup_phone_number": "+16505555555",
                "pickup_instructions": "Enter gate code 1234 on the callbox.",
                "pickup_reference_tag": "Order number 61",
                "dropoff_address": "901 Market Street 6th Floor San Francisco, CA 94103",
                "dropoff_business_name": "Wells Fargo SF Downtown",
                "dropoff_phone_number": "+16505555555",
                "dropoff_instructions": "Enter gate code 1234 on the callbox."
            }
        }


class DoorDashDeliveryResponse(BaseModel):
    """Response model for DoorDash delivery operations."""
    id: Optional[str] = None
    external_delivery_id: Optional[str] = None
    delivery_status: Optional[str] = None
    tracking_url: Optional[str] = None
    currency: Optional[str] = None
    dropoff_deadline: Optional[str] = None
    pickup_deadline: Optional[str] = None
    pickup_address: Optional[str] = None
    dropoff_address: Optional[str] = None
    actual_pickup_time: Optional[str] = None
    actual_dropoff_time: Optional[str] = None
    estimated_pickup_time: Optional[str] = None
    estimated_dropoff_time: Optional[str] = None
    
    class Config:
        # Allow extra fields from DoorDash API that we haven't defined
        extra = "allow"
        json_schema_extra = {
            "example": {
                "id": "d2f7b3c4-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
                "external_delivery_id": "D-12345",
                "delivery_status": "delivery_created",
                "tracking_url": "https://track.doordash.com/delivery/...",
                "currency": "USD",
                "dropoff_deadline": "2024-01-01T12:00:00Z",
                "pickup_deadline": "2024-01-01T11:30:00Z"
            }
        }


class CreateReceiptRequest(BaseModel):
    """Request model for creating a receipt."""
    restaurant_id: str = Field(..., description="MongoDB _id of the restaurant")
    items: List[CartItem] = Field(..., min_items=1, description="List of items in the order")
    delivery_id: Optional[str] = Field(None, description="Optional DoorDash delivery external_delivery_id")
    customer_name: Optional[str] = Field(None, description="Customer name")
    customer_email: Optional[str] = Field(None, description="Customer email")
    customer_phone: Optional[str] = Field(None, description="Customer phone number")
    delivery_address: Optional[str] = Field(None, description="Delivery address")
    
    class Config:
        json_schema_extra = {
            "example": {
                "restaurant_id": "507f1f77bcf86cd799439011",
                "items": [
                    {
                        "item_id": "507f1f77bcf86cd799439012",
                        "quantity": 2
                    },
                    {
                        "item_id": "507f1f77bcf86cd799439013",
                        "quantity": 1
                    }
                ],
                "delivery_id": "D-12345",
                "customer_name": "John Doe",
                "customer_email": "john@example.com",
                "customer_phone": "+16505555555",
                "delivery_address": "123 Main St, San Francisco, CA 94103"
            }
        }


class ReceiptItemDetail(BaseModel):
    """Receipt item detail."""
    item_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    quantity: int
    subtotal: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "item_id": "507f1f77bcf86cd799439012",
                "name": "Burger",
                "description": "Delicious burger",
                "price": 12.99,
                "quantity": 2,
                "subtotal": 25.98
            }
        }


class ReceiptResponse(BaseModel):
    """Receipt response model."""
    _id: str
    receipt_id: str
    restaurant_id: str
    restaurant_name: Optional[str] = None
    items: List[ReceiptItemDetail]
    subtotal: float
    delivery_fee: Optional[float] = None
    tax: Optional[float] = None
    total: float
    delivery_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    delivery_address: Optional[str] = None
    created_at: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439014",
                "receipt_id": "RCP-20240101-001",
                "restaurant_id": "507f1f77bcf86cd799439011",
                "restaurant_name": "Example Restaurant",
                "items": [
                    {
                        "item_id": "507f1f77bcf86cd799439012",
                        "name": "Burger",
                        "price": 12.99,
                        "quantity": 2,
                        "subtotal": 25.98
                    }
                ],
                "subtotal": 25.98,
                "delivery_fee": 2.99,
                "tax": 2.21,
                "total": 31.18,
                "delivery_id": "D-12345",
                "customer_name": "John Doe",
                "customer_email": "john@example.com",
                "customer_phone": "+16505555555",
                "delivery_address": "123 Main St, San Francisco, CA 94103",
                "created_at": "2024-01-01T12:00:00Z"
            }
        }


class AgentRequest(BaseModel):
    """Request model for agent chat endpoint."""
    prompt: str = Field(..., description="User prompt/question for the agent")
    thread_id: Optional[str] = Field(None, description="Optional thread ID to continue a conversation. If not provided, a new thread will be created.")
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "What's the weather like today?",
                "thread_id": "thread_abc123"
            }
        }


class AgentResponse(BaseModel):
    """Response model for agent chat endpoint."""
    response: str = Field(..., description="Agent's response to the user prompt")
    thread_id: str = Field(..., description="Thread ID for continuing this conversation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "I'd be happy to help you with that!",
                "thread_id": "thread_abc123"
            }
        }
