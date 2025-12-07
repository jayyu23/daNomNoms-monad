"""DoorDash service layer with business logic."""
import os
import jwt
import jwt.utils
import time
import math
from typing import Dict, Any
from dotenv import load_dotenv
from fastapi import HTTPException
from models import DoorDashCreateDeliveryRequest, DoorDashDeliveryResponse
import requests

# Load environment variables from .env file
load_dotenv()

# DoorDash API base URL
DOORDASH_API_BASE_URL = "https://openapi.doordash.com/drive/v2"


def create_jwt(developer_id: str, key_id: str, signing_secret: str) -> str:
    """
    Create a JWT token for DoorDash API authentication.
    
    Args:
        developer_id: DoorDash developer ID
        key_id: DoorDash key ID
        signing_secret: DoorDash signing secret (base64url encoded)
    
    Returns:
        Encoded JWT token string
    """
    token = jwt.encode(
        {
            "aud": "doordash",
            "iss": developer_id,
            "kid": key_id,
            "exp": str(math.floor(time.time() + 300)),
            "iat": str(math.floor(time.time())),
        },
        jwt.utils.base64url_decode(signing_secret),
        algorithm="HS256",
        headers={"dd-ver": "DD-JWT-V1"}
    )
    return token


def get_jwt_token() -> str:
    """
    Get JWT token for DoorDash API authentication.
    
    Returns:
        JWT token string
        
    Raises:
        HTTPException: If required environment variables are missing
    """
    developer_id = os.getenv("DOORDASH_DEVELOPER_ID")
    key_id = os.getenv("DOORDASH_KEY_ID")
    signing_secret = os.getenv("DOORDASH_SIGNING_SECRET")
    
    if not developer_id or not key_id or not signing_secret:
        raise HTTPException(
            status_code=500,
            detail="Missing required DoorDash credentials. Please check your .env file."
        )
    
    return create_jwt(developer_id, key_id, signing_secret)


def create_delivery(request: DoorDashCreateDeliveryRequest) -> Dict[str, Any]:
    """
    Create a new DoorDash delivery.
    
    Args:
        request: DoorDash delivery creation request
        
    Returns:
        Dictionary with delivery details
        
    Raises:
        HTTPException: If delivery creation fails
    """
    try:
        # Get JWT token
        token = get_jwt_token()
        
        # Prepare request body
        request_body = {
            "external_delivery_id": request.external_delivery_id,
            "pickup_address": request.pickup_address,
            "pickup_business_name": request.pickup_business_name,
            "pickup_phone_number": request.pickup_phone_number,
            "dropoff_address": request.dropoff_address,
            "dropoff_phone_number": request.dropoff_phone_number,
        }
        
        # Add optional fields if provided
        if request.pickup_instructions:
            request_body["pickup_instructions"] = request.pickup_instructions
        if request.pickup_reference_tag:
            request_body["pickup_reference_tag"] = request.pickup_reference_tag
        if request.dropoff_business_name:
            request_body["dropoff_business_name"] = request.dropoff_business_name
        if request.dropoff_instructions:
            request_body["dropoff_instructions"] = request.dropoff_instructions
        if request.dropoff_contact_given_name:
            request_body["dropoff_contact_given_name"] = request.dropoff_contact_given_name
        if request.dropoff_contact_family_name:
            request_body["dropoff_contact_family_name"] = request.dropoff_contact_family_name
        if request.order_value:
            request_body["order_value"] = request.order_value
        
        # Make request to DoorDash API
        url = f"{DOORDASH_API_BASE_URL}/deliveries"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=request_body, headers=headers, timeout=30)
        
        # Handle response
        if response.status_code == 201 or response.status_code == 200:
            delivery = DoorDashDeliveryResponse(**response.json())
            return delivery.dict()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"DoorDash API error: {response.text}"
            )
            
    except HTTPException:
        raise
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with DoorDash API: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error creating delivery: {str(e)}"
        )


def track_delivery(external_delivery_id: str) -> Dict[str, Any]:
    """
    Get the status of a DoorDash delivery by external delivery ID.
    
    Args:
        external_delivery_id: The external delivery ID used when creating the delivery
        
    Returns:
        Dictionary with current delivery status and details
        
    Raises:
        HTTPException: If delivery not found or tracking fails
    """
    try:
        # Get JWT token
        token = get_jwt_token()
        
        # Make request to DoorDash API
        url = f"{DOORDASH_API_BASE_URL}/deliveries/{external_delivery_id}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        
        # Handle response
        if response.status_code == 200:
            response_data = response.json()
            # Return the response, preserving all fields from DoorDash
            delivery = DoorDashDeliveryResponse(**response_data)
            return delivery.dict()
        elif response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"Delivery with external_delivery_id '{external_delivery_id}' not found"
            )
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"DoorDash API error: {response.text}"
            )
            
    except HTTPException:
        raise
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with DoorDash API: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error tracking delivery: {str(e)}"
        )

