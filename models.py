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

