"""
DoorDash delivery API endpoints.
"""
from fastapi import APIRouter, HTTPException
from models import DoorDashCreateDeliveryRequest, DoorDashDeliveryResponse
from services import doordash_service

router = APIRouter(prefix="/api/doordash", tags=["doordash"])


@router.post("/deliveries", response_model=DoorDashDeliveryResponse)
def doordash_create_delivery(request: DoorDashCreateDeliveryRequest):
    """
    Create a new DoorDash delivery.
    
    This endpoint creates a delivery request through the DoorDash Drive API.
    You can track the delivery status using the Delivery Simulator in the DoorDash Developer Portal.
    
    Args:
        request: DoorDash delivery creation request
        
    Returns:
        DoorDash delivery response with delivery details
        
    Example curl request:
    ```bash
    curl -X POST http://localhost:8000/api/doordash/deliveries \
      -H "Content-Type: application/json" \
      -d '{
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
      }'
    ```
    """
    try:
        result = doordash_service.create_delivery(request)
        return DoorDashDeliveryResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error creating delivery: {str(e)}"
        )


@router.get("/deliveries/{external_delivery_id}", response_model=DoorDashDeliveryResponse)
def doordash_track_delivery_status(external_delivery_id: str):
    """
    Get the status of a DoorDash delivery by external delivery ID.
    
    This endpoint retrieves the current status and details of a delivery
    that was previously created through the create_delivery endpoint.
    
    Args:
        external_delivery_id: The external delivery ID used when creating the delivery
        
    Returns:
        DoorDash delivery response with current delivery status and details
        
    Example curl request:
    ```bash
    curl "http://localhost:8000/api/doordash/deliveries/D-12345"
    ```
    """
    try:
        result = doordash_service.track_delivery(external_delivery_id)
        return DoorDashDeliveryResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error tracking delivery: {str(e)}"
        )
