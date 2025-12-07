"""
Agent API endpoints for GPT-4o-mini integration with Actions (function calling).
"""
import os
import uuid
import json
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from openai import OpenAI
from models import (
    AgentRequest, 
    AgentResponse,
    BuildCartRequest,
    CostEstimateRequest,
    CreateReceiptRequest,
    DoorDashCreateDeliveryRequest,
    CartItem
)
from services import restaurant_service, doordash_service
from database import db_service

# Load environment variables from .env file
load_dotenv()

router = APIRouter(prefix="/api/agent", tags=["agent"])


def resolve_restaurant_name_to_id(restaurant_name: str) -> str:
    """
    Resolve restaurant name to restaurant ID.
    
    Args:
        restaurant_name: Name of the restaurant
        
    Returns:
        Restaurant MongoDB _id
        
    Raises:
        ValueError: If restaurant not found
    """
    restaurant = db_service.get_restaurant_by_name(restaurant_name)
    if not restaurant:
        raise ValueError(f"Restaurant '{restaurant_name}' not found")
    return str(restaurant['_id'])


def resolve_item_name_to_id(restaurant_name: str, item_name: str) -> str:
    """
    Resolve item name to item ID within a restaurant.
    
    Args:
        restaurant_name: Name of the restaurant
        item_name: Name of the menu item
        
    Returns:
        Item MongoDB _id
        
    Raises:
        ValueError: If restaurant or item not found
    """
    restaurant = db_service.get_restaurant_by_name(restaurant_name)
    if not restaurant:
        raise ValueError(f"Restaurant '{restaurant_name}' not found")
    
    restaurant_id = str(restaurant['_id'])
    item = db_service.get_item_by_name(restaurant_id, item_name)
    if not item:
        raise ValueError(f"Item '{item_name}' not found in restaurant '{restaurant_name}'")
    
    return str(item['_id'])


def get_openai_client() -> OpenAI:
    """
    Get OpenAI client instance with API key from environment.
    
    Returns:
        OpenAI client instance
        
    Raises:
        HTTPException: If OPEN_AI_API_KEY is not found in environment variables
    """
    api_key = os.getenv("OPEN_AI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OPEN_AI_API_KEY not found in environment variables. Please check your .env file."
        )
    return OpenAI(api_key=api_key)


def get_gpt_tools() -> List[Dict[str, Any]]:
    """
    Define GPT Actions (tools) for all available API endpoints.
    
    Returns:
        List of tool definitions for OpenAI function calling
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "list_restaurants",
                "description": "List all restaurants with pagination. CRITICAL: When searching for specific cuisines (e.g., Japanese, sushi, pizza), you MUST use limit=100 to get ALL restaurants. Restaurant cuisine information is in the 'description' field (e.g., '$ • Japanese, Fast Casual' or '$$ • Sushi, Salads'). You must search through all restaurants by calling with limit=100, then filter the results by searching the description field for the cuisine type.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of restaurants to return (1-100, default: 100). MANDATORY: When searching for specific cuisines (Japanese, sushi, Italian, etc.), you MUST use limit=100 to get ALL restaurants. Using a smaller limit (like 10 or 50) will cause you to miss restaurants.",
                            "minimum": 1,
                            "maximum": 100
                        },
                        "skip": {
                            "type": "integer",
                            "description": "Number of restaurants to skip for pagination (default: 0)",
                            "minimum": 0
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_restaurant_menu",
                "description": "Get menu items for a specific restaurant by restaurant name. Use the restaurant name directly (e.g., 'U ME', 'Denny\\'s', 'Wasabi Saratoga'). The search is case-insensitive and will find exact or partial matches.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "restaurant_name": {
                            "type": "string",
                            "description": "Name of the restaurant (e.g., 'U ME', 'Denny\\'s', 'Wasabi Saratoga')"
                        }
                    },
                    "required": ["restaurant_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_menu_item",
                "description": "Get details of a specific menu item by restaurant name and item name. Use human-friendly names (e.g., restaurant_name: 'U ME', item_name: 'California Roll').",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "restaurant_name": {
                            "type": "string",
                            "description": "Name of the restaurant (e.g., 'U ME', 'Denny's', 'Wasabi Saratoga')"
                        },
                        "item_name": {
                            "type": "string",
                            "description": "Name of the menu item (e.g., 'California Roll', 'Burger', 'Pad Thai')"
                        }
                    },
                    "required": ["restaurant_name", "item_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "build_cart",
                "description": "Build a shopping cart with items from a restaurant using restaurant and item names. Use human-friendly names (e.g., restaurant_name: 'U ME', items with item_name: 'California Roll').",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "restaurant_name": {
                            "type": "string",
                            "description": "Name of the restaurant (e.g., 'U ME', 'Denny's', 'Wasabi Saratoga')"
                        },
                        "items": {
                            "type": "array",
                            "description": "List of items to add to cart using item names",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "item_name": {
                                        "type": "string",
                                        "description": "Name of the menu item (e.g., 'California Roll', 'Burger', 'Pad Thai')"
                                    },
                                    "quantity": {
                                        "type": "integer",
                                        "description": "Quantity of the item (minimum 1)",
                                        "minimum": 1
                                    }
                                },
                                "required": ["item_name", "quantity"]
                            },
                            "minItems": 1
                        }
                    },
                    "required": ["restaurant_name", "items"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "compute_cost_estimate",
                "description": "Compute cost estimate for a cart using restaurant and item names. Use human-friendly names (e.g., restaurant_name: 'U ME', items with item_name: 'California Roll').",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "restaurant_name": {
                            "type": "string",
                            "description": "Name of the restaurant (e.g., 'U ME', 'Denny's', 'Wasabi Saratoga')"
                        },
                        "items": {
                            "type": "array",
                            "description": "List of items in cart using item names",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "item_name": {
                                        "type": "string",
                                        "description": "Name of the menu item (e.g., 'California Roll', 'Burger', 'Pad Thai')"
                                    },
                                    "quantity": {
                                        "type": "integer",
                                        "description": "Quantity of the item (minimum 1)",
                                        "minimum": 1
                                    }
                                },
                                "required": ["item_name", "quantity"]
                            },
                            "minItems": 1
                        }
                    },
                    "required": ["restaurant_name", "items"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_receipt",
                "description": "Create a receipt for a completed order using restaurant and item names. Use human-friendly names (e.g., restaurant_name: 'U ME', items with item_name: 'California Roll').",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "restaurant_name": {
                            "type": "string",
                            "description": "Name of the restaurant (e.g., 'U ME', 'Denny's', 'Wasabi Saratoga')"
                        },
                        "items": {
                            "type": "array",
                            "description": "List of items in the order using item names",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "item_name": {
                                        "type": "string",
                                        "description": "Name of the menu item (e.g., 'California Roll', 'Burger', 'Pad Thai')"
                                    },
                                    "quantity": {
                                        "type": "integer",
                                        "description": "Quantity of the item (minimum 1)",
                                        "minimum": 1
                                    }
                                },
                                "required": ["item_name", "quantity"]
                            },
                            "minItems": 1
                        },
                        "delivery_id": {
                            "type": "string",
                            "description": "Optional DoorDash delivery external_delivery_id if linked to a delivery"
                        },
                        "customer_name": {
                            "type": "string",
                            "description": "Customer name"
                        },
                        "customer_email": {
                            "type": "string",
                            "description": "Customer email"
                        },
                        "customer_phone": {
                            "type": "string",
                            "description": "Customer phone number"
                        },
                        "delivery_address": {
                            "type": "string",
                            "description": "Delivery address"
                        }
                    },
                    "required": ["restaurant_name", "items"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_delivery",
                "description": "Create a new DoorDash delivery. Use this to set up delivery for an order.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "external_delivery_id": {
                            "type": "string",
                            "description": "Unique identifier for the delivery"
                        },
                        "pickup_address": {
                            "type": "string",
                            "description": "Pickup address"
                        },
                        "pickup_business_name": {
                            "type": "string",
                            "description": "Business name for pickup location"
                        },
                        "pickup_phone_number": {
                            "type": "string",
                            "description": "Phone number for pickup location"
                        },
                        "dropoff_address": {
                            "type": "string",
                            "description": "Dropoff address"
                        },
                        "dropoff_phone_number": {
                            "type": "string",
                            "description": "Phone number for dropoff location"
                        },
                        "pickup_instructions": {
                            "type": "string",
                            "description": "Special instructions for pickup"
                        },
                        "pickup_reference_tag": {
                            "type": "string",
                            "description": "Reference tag for pickup"
                        },
                        "dropoff_business_name": {
                            "type": "string",
                            "description": "Business name for dropoff location"
                        },
                        "dropoff_instructions": {
                            "type": "string",
                            "description": "Special instructions for dropoff"
                        },
                        "dropoff_contact_given_name": {
                            "type": "string",
                            "description": "Contact first name"
                        },
                        "dropoff_contact_family_name": {
                            "type": "string",
                            "description": "Contact last name"
                        },
                        "order_value": {
                            "type": "integer",
                            "description": "Order value in cents"
                        }
                    },
                    "required": [
                        "external_delivery_id",
                        "pickup_address",
                        "pickup_business_name",
                        "pickup_phone_number",
                        "dropoff_address",
                        "dropoff_phone_number"
                    ]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "track_delivery",
                "description": "Get the status of a DoorDash delivery by external delivery ID. Use this to check delivery status after creating a delivery.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "external_delivery_id": {
                            "type": "string",
                            "description": "The external delivery ID used when creating the delivery"
                        }
                    },
                    "required": ["external_delivery_id"]
                }
            }
        }
    ]


def execute_function_call(function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a function call by directly calling the service layer.
    
    Args:
        function_name: Name of the function to call
        arguments: Function arguments
        
    Returns:
        Function execution result
    """
    try:
        if function_name == "list_restaurants":
            # Default to 100 to get all restaurants, allow up to 100
            limit = min(arguments.get("limit", 100), 100)
            skip = arguments.get("skip", 0)
            result = restaurant_service.list_restaurants(limit=limit, skip=skip)
            
            # For large lists, return minimal data to prevent token overflow
            # But keep description field for cuisine searching
            if isinstance(result, dict) and "restaurants" in result:
                restaurants = result["restaurants"]
                # Always return minimal data when we have many restaurants to keep response manageable
                if len(restaurants) > 20:
                    # Return minimal data: only _id, name, description for filtering
                    minimal_restaurants = []
                    for r in restaurants:
                        minimal_restaurants.append({
                            "_id": r.get("_id"),
                            "name": r.get("name"),
                            "description": r.get("description"),
                            "store_id": r.get("store_id")
                        })
                    result["restaurants"] = minimal_restaurants
                    result["truncated"] = True
                    result["note"] = f"Showing minimal data (id, name, description) for {len(minimal_restaurants)} restaurants. Use get_restaurant_menu for full details."
            
            return result
            
        elif function_name == "get_restaurant_menu":
            restaurant_name = arguments.get("restaurant_name")
            if not restaurant_name:
                return {"error": "restaurant_name is required"}
            result = restaurant_service.get_restaurant_menu_by_name(restaurant_name)
            # Limit large responses to prevent token overflow
            if isinstance(result, dict) and "items" in result:
                if len(result["items"]) > 20:
                    result["items"] = result["items"][:20]
                    result["total_items"] = min(result.get("total_items", 0), 20)
            return result
            
        elif function_name == "get_menu_item":
            restaurant_name = arguments.get("restaurant_name")
            item_name = arguments.get("item_name")
            if not restaurant_name or not item_name:
                return {"error": "restaurant_name and item_name are required"}
            try:
                item_id = resolve_item_name_to_id(restaurant_name, item_name)
                return restaurant_service.get_menu_item(item_id)
            except ValueError as e:
                return {"error": str(e)}
            
        elif function_name == "build_cart":
            restaurant_name = arguments.get("restaurant_name")
            items = arguments.get("items", [])
            if not restaurant_name or not items:
                return {"error": "restaurant_name and items are required"}
            
            try:
                # Resolve restaurant name to ID
                restaurant_id = resolve_restaurant_name_to_id(restaurant_name)
                
                # Resolve item names to IDs
                resolved_items = []
                for item in items:
                    item_name = item.get("item_name")
                    quantity = item.get("quantity")
                    if not item_name or not quantity:
                        return {"error": "Each item must have item_name and quantity"}
                    item_id = resolve_item_name_to_id(restaurant_name, item_name)
                    resolved_items.append({"item_id": item_id, "quantity": quantity})
                
                # Create request with resolved IDs
                request = BuildCartRequest(restaurant_id=restaurant_id, items=[CartItem(**item) for item in resolved_items])
                return restaurant_service.build_cart(request)
            except ValueError as e:
                return {"error": str(e)}
            except Exception as e:
                return {"error": f"Invalid request parameters: {str(e)}"}
            
        elif function_name == "compute_cost_estimate":
            restaurant_name = arguments.get("restaurant_name")
            items = arguments.get("items", [])
            if not restaurant_name or not items:
                return {"error": "restaurant_name and items are required"}
            
            try:
                # Resolve restaurant name to ID
                restaurant_id = resolve_restaurant_name_to_id(restaurant_name)
                
                # Resolve item names to IDs
                resolved_items = []
                for item in items:
                    item_name = item.get("item_name")
                    quantity = item.get("quantity")
                    if not item_name or not quantity:
                        return {"error": "Each item must have item_name and quantity"}
                    item_id = resolve_item_name_to_id(restaurant_name, item_name)
                    resolved_items.append({"item_id": item_id, "quantity": quantity})
                
                # Create request with resolved IDs
                request = CostEstimateRequest(restaurant_id=restaurant_id, items=[CartItem(**item) for item in resolved_items])
                return restaurant_service.compute_cost_estimate(request)
            except ValueError as e:
                return {"error": str(e)}
            except Exception as e:
                return {"error": f"Invalid request parameters: {str(e)}"}
            
        elif function_name == "create_receipt":
            restaurant_name = arguments.get("restaurant_name")
            items = arguments.get("items", [])
            if not restaurant_name or not items:
                return {"error": "restaurant_name and items are required"}
            
            try:
                # Resolve restaurant name to ID
                restaurant_id = resolve_restaurant_name_to_id(restaurant_name)
                
                # Resolve item names to IDs
                resolved_items = []
                for item in items:
                    item_name = item.get("item_name")
                    quantity = item.get("quantity")
                    if not item_name or not quantity:
                        return {"error": "Each item must have item_name and quantity"}
                    item_id = resolve_item_name_to_id(restaurant_name, item_name)
                    resolved_items.append({"item_id": item_id, "quantity": quantity})
                
                # Create request with resolved IDs and other fields
                receipt_args = {
                    "restaurant_id": restaurant_id,
                    "items": [CartItem(**item) for item in resolved_items]
                }
                # Add optional fields if provided
                for field in ["delivery_id", "customer_name", "customer_email", "customer_phone", "delivery_address"]:
                    if field in arguments:
                        receipt_args[field] = arguments[field]
                
                request = CreateReceiptRequest(**receipt_args)
                return restaurant_service.create_receipt(request)
            except ValueError as e:
                return {"error": str(e)}
            except Exception as e:
                return {"error": f"Invalid request parameters: {str(e)}"}
            
        elif function_name == "create_delivery":
            try:
                request = DoorDashCreateDeliveryRequest(**arguments)
            except Exception as e:
                return {"error": f"Invalid request parameters: {str(e)}"}
            return doordash_service.create_delivery(request)
            
        elif function_name == "track_delivery":
            external_delivery_id = arguments.get("external_delivery_id")
            if not external_delivery_id:
                return {"error": "external_delivery_id is required"}
            return doordash_service.track_delivery(external_delivery_id)
            
        else:
            return {"error": f"Unknown function: {function_name}"}
            
    except HTTPException as e:
        return {
            "error": e.detail,
            "error_type": "http_exception",
            "status_code": e.status_code
        }
    except Exception as e:
        return {
            "error": f"Unexpected error: {str(e)}",
            "error_type": "unexpected_error"
        }


# In-memory storage for conversation threads
conversation_threads: Dict[str, List[Dict[str, Any]]] = {}


def trim_conversation_history(messages: List[Dict[str, Any]], max_messages: int = 20) -> List[Dict[str, Any]]:
    """
    Trim conversation history to keep only the most recent messages.
    This prevents token overflow by maintaining a sliding window of recent messages.
    """
    if len(messages) <= max_messages:
        return messages
    
    system_msgs = [msg for msg in messages if msg.get("role") == "system"]
    non_system_msgs = [msg for msg in messages if msg.get("role") != "system"]
    trimmed_non_system = non_system_msgs[-max_messages:] if len(non_system_msgs) > max_messages else non_system_msgs
    
    return system_msgs + trimmed_non_system


def truncate_large_content(content: str, max_length: int = 3000) -> str:
    """Truncate large content strings to prevent token overflow."""
    if isinstance(content, str) and len(content) > max_length:
        return content[:max_length] + "\n\n[Content truncated due to length...]"
    return content


def get_or_create_thread(thread_id: str) -> List[Dict[str, Any]]:
    """Get conversation history for a thread, or create a new thread if it doesn't exist."""
    if thread_id not in conversation_threads:
        conversation_threads[thread_id] = []
    return conversation_threads[thread_id]


def generate_thread_id() -> str:
    """Generate a new unique thread ID."""
    return f"thread_{uuid.uuid4().hex[:12]}"


@router.post("/chat", response_model=AgentResponse)
async def agent_chat(request: AgentRequest):
    """
    Chat with GPT-4o-mini agent with conversation memory and GPT Actions.
    """
    try:
        client = get_openai_client()
        thread_id = request.thread_id or generate_thread_id()
        conversation_history = get_or_create_thread(thread_id)
        
        # Trim conversation history to prevent token overflow
        conversation_history = trim_conversation_history(conversation_history, max_messages=20)
        conversation_threads[thread_id] = conversation_history
        
        # Add user message
        conversation_history.append({
            "role": "user",
            "content": request.prompt
        })
        
        tools = get_gpt_tools()
        
        system_message = {
            "role": "system",
            "content": "You are a helpful assistant for the DaNomNoms food delivery service. You can help users browse restaurants, view menus, build carts, create orders, and manage deliveries. Use the available functions to interact with the API when needed. CRITICAL SEARCH INSTRUCTIONS FOR CUISINE REQUESTS: When a user asks for specific cuisine types (e.g., 'Japanese restaurants', 'I want sushi', 'show me Italian places'), you MUST: 1) FIRST call list_restaurants with limit=100 (not 10, not 50, but 100) to get ALL available restaurants, 2) EXAMINE each restaurant's 'description' field carefully - cuisine types are listed there (e.g., 'Japanese, Fast Casual', 'Sushi, Salads', 'Japanese, Sushi'), 3) FILTER the results to only show restaurants whose description contains the requested cuisine keyword (case-insensitive search), 4) PRESENT the filtered list to the user. Example: If user asks for Japanese, search for 'Japanese' or 'sushi' in description fields. IMPORTANT: Restaurant descriptions look like '$ • Japanese, Fast Casual' or '$$ • Sushi, Salads' - the cuisine appears after the price and bullet. Never say a cuisine is unavailable until you've searched through ALL 100 restaurants. If you receive a list of restaurants, you MUST search through ALL of them before concluding none match. RESTAURANT MENU REQUESTS: When a user asks for a menu by restaurant name (e.g., 'Show me U ME menu', 'What does Denny's have?'), you can directly call get_restaurant_menu with the restaurant_name parameter. You don't need to look up IDs - just use the restaurant name the user provides. The search is case-insensitive and handles exact or partial matches. CRITICAL: When function calls return errors (check for 'success: false' or 'error' fields), you MUST show the user the exact error message from the function result. Do NOT say 'temporary issue' or 'unable to retrieve' - instead, quote the actual error message so the user knows what went wrong."
        }
        
        messages = [system_message] if len(conversation_history) == 1 else []
        messages.extend(conversation_history)
        
        max_iterations = 10
        iteration = 0
        final_response = ""
        
        while iteration < max_iterations:
            api_messages = []
            for msg in messages:
                if msg.get("role") == "tool":
                    api_messages.append({
                        "role": "tool",
                        "tool_call_id": msg.get("tool_call_id"),
                        "content": msg.get("content")
                    })
                elif msg.get("role") == "assistant" and msg.get("tool_calls"):
                    api_messages.append({
                        "role": "assistant",
                        "content": msg.get("content") or None,
                        "tool_calls": msg.get("tool_calls")
                    })
                else:
                    api_messages.append({
                        "role": msg.get("role"),
                        "content": msg.get("content")
                    })
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=api_messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.7,
                max_tokens=1000
            )
            
            assistant_message = response.choices[0].message
            
            assistant_msg_dict = {
                "role": "assistant",
                "content": assistant_message.content
            }
            
            if assistant_message.tool_calls:
                assistant_msg_dict["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    } for tc in assistant_message.tool_calls
                ]
            
            messages.append(assistant_msg_dict)
            
            if not assistant_message.tool_calls:
                final_response = assistant_message.content or ""
                break
            
            # Execute tool calls
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                try:
                    function_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    function_args = {}
                
                # Execute function call
                function_result = execute_function_call(function_name, function_args)
                
                # Check if result contains an error and format it appropriately
                if isinstance(function_result, dict) and "error" in function_result:
                    # Format error for better LLM understanding
                    error_msg = function_result.get("error", "Unknown error")
                    error_type = function_result.get("error_type", "unknown")
                    function_result = {
                        "success": False,
                        "error": error_msg,
                        "error_type": error_type,
                        "suggestion": "Please try again. If this is the first request after inactivity, the server may be waking up (can take 50+ seconds on free tier)."
                    }
                
                result_json = json.dumps(function_result)
                # Use larger limit for restaurant lists to allow filtering
                max_length = 15000 if function_name == "list_restaurants" else 5000
                truncated_result = truncate_large_content(result_json, max_length=max_length)
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": truncated_result
                })
            
            iteration += 1
        
        if not final_response:
            for msg in reversed(messages):
                if msg.get("role") == "assistant" and msg.get("content"):
                    final_response = msg.get("content")
                    break
        
        # If still no response, check for errors in tool results
        if not final_response:
            error_messages = []
            for msg in messages:
                if msg.get("role") == "tool":
                    try:
                        content = json.loads(msg.get("content", "{}"))
                        if isinstance(content, dict) and "error" in content:
                            error_messages.append(content.get("error", "Unknown error"))
                    except:
                        pass
            
            if error_messages:
                final_response = f"I encountered an error: {error_messages[-1]}"
            else:
                final_response = "I apologize, but I encountered an issue processing your request. The agent may have exceeded the maximum iterations or encountered an unexpected error."
        
        updated_history = [msg for msg in messages if msg.get("role") != "system"]
        conversation_threads[thread_id] = trim_conversation_history(updated_history, max_messages=20)
        
        return AgentResponse(
            response=final_response,
            thread_id=thread_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"Error communicating with OpenAI API: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(
            status_code=500,
            detail=error_detail
        )
