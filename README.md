# daNomNoms-monad

Monad x402 SF Hackathon Project

## Project Overview

DaNomNoms is a full-stack food delivery platform built for the Monad blockchain ecosystem. The project demonstrates seamless integration of AI-powered conversational ordering, blockchain-based micropayments via x402 protocol, and traditional delivery fulfillment through DoorDash.

### Key Features

- **AI-Powered Ordering**: GPT-4o-mini powered conversational agent that helps users browse restaurants, view menus, build carts, and place orders through natural language
- **Blockchain Payments**: Secure micropayments on Monad testnet using x402 protocol for frictionless payment processing
- **Restaurant Management**: Comprehensive restaurant and menu management with MongoDB backend
- **Delivery Integration**: Full DoorDash Drive API integration for order fulfillment and real-time delivery tracking
- **Modern Tech Stack**: FastAPI backend with Next.js frontend, featuring real-time chat interface and responsive design

### Architecture

- **Backend API** (This Repository): FastAPI-based REST API with MongoDB, OpenAI integration, and DoorDash API integration
- **Frontend Application**: Next.js web application with AI chat interface, wallet integration, and payment processing
  - Frontend Repository: [danomnoms-frontend-v0](https://github.com/jayyu23/danomnoms-frontend-v0)

### Tech Stack

**Backend:**
- FastAPI (Python web framework)
- MongoDB (Database)
- OpenAI GPT-4o-mini (AI agent)
- DoorDash Drive API (Delivery fulfillment)
- Pydantic (Data validation)

**Frontend:**
- Next.js 16 (React framework)
- TypeScript
- Tailwind CSS
- Wagmi & Viem (Ethereum wallet integration)
- Thirdweb x402 (Micropayment protocol)
- React Markdown (Message rendering)

A REST API for the DaNomNoms food delivery service, integrating with DoorDash for delivery fulfillment.

## Demo

![DaNomNoms Demo](./photo.png)

## Table of Contents

- [Project Overview](#project-overview)
- [Frontend Application](#frontend-application)
- [Setup](#setup)
- [Environment Variables](#environment-variables)
- [Running the Server](#running-the-server)
- [API Documentation](#api-documentation)
  - [General Endpoints](#general-endpoints)
  - [Restaurant Endpoints](#restaurant-endpoints)
  - [DoorDash Delivery Endpoints](#doordash-delivery-endpoints)
  - [Agent Endpoints](#agent-endpoints)

## Frontend Application

The frontend application provides a modern web interface for the DaNomNoms platform with the following features:

- **Interactive AI Chat Interface**: Natural language conversation with GPT-4o-mini agent for browsing restaurants, viewing menus, and placing orders
- **Wallet Integration**: Seamless connection to Monad testnet wallets using Wagmi and Viem
- **x402 Micropayments**: Secure, low-cost payment processing using Thirdweb's x402 protocol
- **Real-time Order Tracking**: Live delivery status updates integrated with DoorDash
- **Responsive Design**: Mobile-first design with Tailwind CSS for optimal experience across devices

**Frontend Repository**: 
- The frontend code is included in this monorepo at [`./danomnoms-frontend-v0/`](./danomnoms-frontend-v0/)
- If the frontend is hosted in a separate repository, update this section with the repository URL

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the root directory (see [Environment Variables](#environment-variables))

3. Ensure MongoDB is running and configured (check `database.py` for connection details)

4. Run the server:
```bash
uvicorn app:app --reload
```

The API will be available at `https://danomnoms-api.onrender.com`

Interactive API documentation (Swagger UI) is available at `https://danomnoms-api.onrender.com/docs`
Alternative API documentation (ReDoc) is available at `https://danomnoms-api.onrender.com/redoc`

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# MongoDB connection string
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority

# DoorDash API credentials
DOORDASH_DEVELOPER_ID=your_developer_id
DOORDASH_KEY_ID=your_key_id
DOORDASH_SIGNING_SECRET=your_signing_secret

# OpenAI API key for agent endpoint
OPEN_AI_API_KEY=your_openai_api_key
```

**MongoDB Setup:**
- Get a free MongoDB database from [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- Create a cluster and get your connection string
- Replace `username`, `password`, and `cluster` with your actual values

**DoorDash Credentials:**
- Get your DoorDash credentials from the [DoorDash Developer Portal](https://developer.doordash.com/)
- The `DOORDASH_SIGNING_SECRET` should be base64url encoded

**OpenAI API Key:**
- Get your API key from the [OpenAI Platform](https://platform.openai.com/api-keys)
- Required for the agent chat endpoint using GPT-4o-mini

## Running the Server

```bash
# Development mode with auto-reload
uvicorn app:app --reload

# Production mode
uvicorn app:app --host 0.0.0.0 --port 8000
```

## Deployment to Render

This application can be easily deployed to [Render](https://render.com) for production hosting.

### Prerequisites

1. A [Render account](https://render.com) (free tier available)
2. A MongoDB database (recommended: [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) free tier)
3. Your DoorDash API credentials

### Deployment Steps

#### Option 1: Using Render Blueprint (Recommended)

1. **Fork/Push your repository to GitHub** (if not already done)

2. **Go to Render Dashboard** → Click "New +" → Select "Blueprint"

3. **Connect your GitHub repository** and select this repository

4. **Render will automatically detect `render.yaml`** and create the service

5. **Set Environment Variables** in the Render dashboard:
   - `MONGODB_URI`: Your MongoDB connection string (e.g., `mongodb+srv://user:pass@cluster.mongodb.net/`)
   - `DOORDASH_DEVELOPER_ID`: Your DoorDash developer ID
   - `DOORDASH_KEY_ID`: Your DoorDash key ID
   - `DOORDASH_SIGNING_SECRET`: Your DoorDash signing secret (base64url encoded)
   - `OPEN_AI_API_KEY`: Your OpenAI API key (for agent chat endpoint)

6. **Deploy!** Render will automatically build and deploy your application

#### Option 2: Manual Setup

1. **Go to Render Dashboard** → Click "New +" → Select "Web Service"

2. **Connect your GitHub repository** and select this repository

3. **Configure the service:**
   - **Name**: `danomnoms-api` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free (or upgrade for production)

4. **Add Environment Variables:**
   - `MONGODB_URI`: Your MongoDB connection string
   - `DOORDASH_DEVELOPER_ID`: Your DoorDash developer ID
   - `DOORDASH_KEY_ID`: Your DoorDash key ID
   - `DOORDASH_SIGNING_SECRET`: Your DoorDash signing secret
   - `OPEN_AI_API_KEY`: Your OpenAI API key (for agent chat endpoint)

5. **Click "Create Web Service"** and wait for deployment

### Post-Deployment

1. **Update CORS settings** in `app.py`:
   - Change `allow_origins=["*"]` to your frontend domain(s)
   - Example: `allow_origins=["https://your-frontend.vercel.app"]`

2. **Access your API:**
   - Your API will be available at: `https://danomnoms-api.onrender.com`
   - API docs: `https://danomnoms-api.onrender.com/docs`
   - Health check: `https://danomnoms-api.onrender.com/health`

### Important Notes

- **Free Tier Limitations**: Render's free tier spins down after 15 minutes of inactivity. The first request after spin-down may take 30-60 seconds. Consider upgrading to a paid plan for production.
- **MongoDB Atlas**: Highly recommended for production. The free tier (M0) provides 512MB storage.
- **Environment Variables**: Never commit `.env` files. All secrets should be set in Render's dashboard.
- **SQLite Database**: The `doordash_data.db` file is not suitable for multi-instance deployments. Consider migrating this data to MongoDB if needed.

### Monitoring

- Check deployment logs in the Render dashboard
- Monitor health endpoint: `GET /health`
- Set up alerts in Render for failed deployments

## API Documentation

Base URL: `https://danomnoms-api.onrender.com`

All endpoints return JSON responses.

### General Endpoints

#### GET `/`

Root endpoint that lists all available API endpoints.

**Response:**
```json
{
  "message": "Welcome to DaNomNoms API",
  "version": "1.0.0",
  "endpoints": {
    "list_restaurants": "GET /api/restaurants/",
    "get_restaurant": "GET /api/restaurants/{restaurant_id}",
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
```

**Example:**
```bash
curl https://danomnoms-api.onrender.com/
```

#### GET `/health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

**Example:**
```bash
curl https://danomnoms-api.onrender.com/health
```

---

### Restaurant Endpoints

All restaurant endpoints are prefixed with `/api/restaurants`

#### GET `/api/restaurants/`

List all restaurants with pagination.

**Query Parameters:**
- `limit` (optional, default: 100, min: 1, max: 1000): Maximum number of restaurants to return
- `skip` (optional, default: 0, min: 0): Number of restaurants to skip (for pagination)

**Response:**
```json
{
  "restaurants": [
    {
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
  ],
  "total": 100,
  "limit": 100,
  "skip": 0
}
```

**Example:**
```bash
curl "https://danomnoms-api.onrender.com/api/restaurants/?limit=10&skip=0"
```

#### GET `/api/restaurants/{restaurant_id}/menu`

Get menu items for a specific restaurant.

**Path Parameters:**
- `restaurant_id` (required): MongoDB `_id` of the restaurant

**Response:**
```json
{
  "restaurant_id": "69347db4fa0aa2fde8fdaeb3",
  "restaurant_name": "Example Restaurant",
  "items": [
    {
      "_id": "507f1f77bcf86cd799439012",
      "store_id": "12345",
      "name": "Burger",
      "description": "Delicious burger",
      "price": 12.99,
      "rating_percent": 95.0,
      "review_count": 50,
      "image_url": "https://example.com/burger.jpg"
    }
  ],
  "total_items": 50
}
```

**Example:**
```bash
curl "https://danomnoms-api.onrender.com/api/restaurants/69347db4fa0aa2fde8fdaeb3/menu"
```

#### GET `/api/restaurants/items/{item_id}`

Get a single menu item by its ID.

**Path Parameters:**
- `item_id` (required): MongoDB `_id` of the menu item

**Response:**
```json
{
  "_id": "507f1f77bcf86cd799439012",
  "store_id": "12345",
  "name": "Burger",
  "description": "Delicious burger",
  "price": 12.99,
  "rating_percent": 95.0,
  "review_count": 50,
  "image_url": "https://example.com/burger.jpg"
}
```

**Example:**
```bash
curl "https://danomnoms-api.onrender.com/api/restaurants/items/69347db5fa0aa2fde8fdaf17"
```

#### POST `/api/restaurants/cart`

Build a shopping cart with items from a restaurant.

**Request Body:**
```json
{
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
}
```

**Response:**
```json
{
  "restaurant_id": "69347db4fa0aa2fde8fdaeb3",
  "restaurant_name": "Example Restaurant",
  "items": [
    {
      "item_id": "69347db5fa0aa2fde8fdaf17",
      "name": "Burger",
      "description": "Delicious burger",
      "price": 12.99,
      "quantity": 2,
      "subtotal": 25.98
    }
  ],
  "subtotal": 25.98,
  "delivery_fee": 2.99,
  "total": 28.97
}
```

**Example:**
```bash
curl -X POST https://danomnoms-api.onrender.com/api/restaurants/cart \
  -H "Content-Type: application/json" \
  -d '{
    "restaurant_id": "69347db4fa0aa2fde8fdaeb3",
    "items": [
      {
        "item_id": "69347db5fa0aa2fde8fdaf17",
        "quantity": 2
      }
    ]
  }'
```

#### POST `/api/restaurants/cost-estimate`

Compute cost estimate for a cart without building the full cart.

**Request Body:**
```json
{
  "restaurant_id": "69347db4fa0aa2fde8fdaeb6",
  "items": [
    {
      "item_id": "69347db5fa0aa2fde8fdafc4",
      "quantity": 2
    }
  ]
}
```

**Response:**
```json
{
  "restaurant_id": "69347db4fa0aa2fde8fdaeb6",
  "restaurant_name": "Example Restaurant",
  "subtotal": 25.98,
  "delivery_fee": 2.99,
  "estimated_total": 30.19,
  "estimated_tax": 2.21
}
```

**Example:**
```bash
curl -X POST https://danomnoms-api.onrender.com/api/restaurants/cost-estimate \
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

#### POST `/api/restaurants/receipts`

Create a receipt for a completed order.

**Request Body:**
```json
{
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
}
```

**Required Fields:**
- `restaurant_id`: MongoDB `_id` of the restaurant
- `items`: List of items in the order (minimum 1 item required)
  - `item_id`: MongoDB `_id` of the menu item
  - `quantity`: Quantity of the item (minimum 1)

**Optional Fields:**
- `delivery_id`: DoorDash delivery external_delivery_id (if linked to a delivery)
- `customer_name`: Customer name
- `customer_email`: Customer email
- `customer_phone`: Customer phone number
- `delivery_address`: Delivery address

**Response:**
```json
{
  "_id": "507f1f77bcf86cd799439014",
  "receipt_id": "RCP-20240101-001",
  "restaurant_id": "69347db4fa0aa2fde8fdaeb3",
  "restaurant_name": "Example Restaurant",
  "items": [
    {
      "item_id": "69347db5fa0aa2fde8fdaf17",
      "name": "Burger",
      "description": "Delicious burger",
      "price": 12.99,
      "quantity": 2,
      "subtotal": 25.98
    },
    {
      "item_id": "69347db5fa0aa2fde8fdaf18",
      "name": "Fries",
      "description": "Crispy fries",
      "price": 4.99,
      "quantity": 1,
      "subtotal": 4.99
    }
  ],
  "subtotal": 30.97,
  "delivery_fee": 2.99,
  "tax": 2.63,
  "total": 36.59,
  "delivery_id": "D-12345",
  "customer_name": "John Doe",
  "customer_email": "john@example.com",
  "customer_phone": "+16505555555",
  "delivery_address": "123 Main St, San Francisco, CA 94103",
  "created_at": "2024-01-01T12:00:00Z"
}
```

**Example:**
```bash
curl -X POST https://danomnoms-api.onrender.com/api/restaurants/receipts \
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

**Note:** 
- The receipt ID is automatically generated in the format `RCP-YYYYMMDD-XXX` where `XXX` is a sequential number for the day
- Tax is calculated at 8.5% of the subtotal
- The receipt is saved to MongoDB and can be retrieved later using the `_id` or `receipt_id`

---

### DoorDash Delivery Endpoints

All DoorDash endpoints are prefixed with `/api/doordash`

**Note:** These endpoints require DoorDash credentials to be configured in your `.env` file. JWT tokens are automatically generated for authentication.

#### POST `/api/doordash/deliveries`

Create a new DoorDash delivery.

**Request Body:**
```json
{
  "external_delivery_id": "D-12345",
  "pickup_address": "901 Market Street 6th Floor San Francisco, CA 94103",
  "pickup_business_name": "Wells Fargo SF Downtown",
  "pickup_phone_number": "+16505555555",
  "pickup_instructions": "Enter gate code 1234 on the callbox.",
  "pickup_reference_tag": "Order number 61",
  "dropoff_address": "901 Market Street 6th Floor San Francisco, CA 94103",
  "dropoff_business_name": "Wells Fargo SF Downtown",
  "dropoff_phone_number": "+16505555555",
  "dropoff_instructions": "Enter gate code 1234 on the callbox.",
  "dropoff_contact_given_name": "John",
  "dropoff_contact_family_name": "Doe",
  "order_value": 5000
}
```

**Required Fields:**
- `external_delivery_id`: Unique identifier for the delivery
- `pickup_address`: Pickup address
- `pickup_business_name`: Business name for pickup location
- `pickup_phone_number`: Phone number for pickup location
- `dropoff_address`: Dropoff address
- `dropoff_phone_number`: Phone number for dropoff location

**Optional Fields:**
- `pickup_instructions`: Special instructions for pickup
- `pickup_reference_tag`: Reference tag for pickup
- `dropoff_business_name`: Business name for dropoff location
- `dropoff_instructions`: Special instructions for dropoff
- `dropoff_contact_given_name`: Contact first name
- `dropoff_contact_family_name`: Contact last name
- `order_value`: Order value in cents

**Response:**
```json
{
  "id": "d2f7b3c4-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
  "external_delivery_id": "D-12345",
  "delivery_status": "created",
  "tracking_url": "https://www.doordash.com/orders/drive?urlCode=...",
  "currency": "USD",
  "dropoff_deadline": null,
  "pickup_deadline": null,
  "pickup_address": "901 Market St Fl 6th, San Francisco CA 94103-1729, United States",
  "dropoff_address": "901 Market St Fl 6th, San Francisco CA 94103-1729, United States",
  "actual_pickup_time": null,
  "actual_dropoff_time": null,
  "estimated_pickup_time": null,
  "estimated_dropoff_time": null
}
```

**Example:**
```bash
curl -X POST https://danomnoms-api.onrender.com/api/doordash/deliveries \
  -H "Content-Type: application/json" \
  -d '{
    "external_delivery_id": "D-12345",
    "pickup_address": "901 Market Street 6th Floor San Francisco, CA 94103",
    "pickup_business_name": "Wells Fargo SF Downtown",
    "pickup_phone_number": "+16505555555",
    "pickup_instructions": "Enter gate code 1234 on the callbox.",
    "dropoff_address": "901 Market Street 6th Floor San Francisco, CA 94103",
    "dropoff_phone_number": "+16505555555",
    "dropoff_instructions": "Enter gate code 1234 on the callbox."
  }'
```

**Note:** You can track the delivery status using the Delivery Simulator in the DoorDash Developer Portal. Some fields (like `estimated_pickup_time`, `actual_pickup_time`) will be populated as the delivery progresses through different stages.

#### GET `/api/doordash/deliveries/{external_delivery_id}`

Get the status of a DoorDash delivery by external delivery ID.

**Path Parameters:**
- `external_delivery_id` (required): The external delivery ID used when creating the delivery

**Response:**
```json
{
  "id": "d2f7b3c4-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
  "external_delivery_id": "D-12345",
  "delivery_status": "enroute_to_pickup",
  "tracking_url": "https://www.doordash.com/orders/drive?urlCode=...",
  "currency": "USD",
  "dropoff_deadline": "2024-01-01T12:00:00Z",
  "pickup_deadline": "2024-01-01T11:30:00Z",
  "pickup_address": "901 Market St Fl 6th, San Francisco CA 94103-1729, United States",
  "dropoff_address": "901 Market St Fl 6th, San Francisco CA 94103-1729, United States",
  "actual_pickup_time": null,
  "actual_dropoff_time": null,
  "estimated_pickup_time": "2024-01-01T11:30:00Z",
  "estimated_dropoff_time": "2024-01-01T12:00:00Z"
}
```

**Example:**
```bash
curl "https://danomnoms-api.onrender.com/api/doordash/deliveries/D-12345"
```

**Delivery Status Values:**
- `created`: Delivery has been created
- `enroute_to_pickup`: Dasher is on the way to pick up the order
- `delivery_confirmed`: Delivery has been confirmed
- `enroute_to_dropoff`: Dasher is on the way to drop off the order
- `delivered`: Delivery has been completed

---

### Agent Endpoints

All agent endpoints are prefixed with `/api/agent`

**Note:** These endpoints require an OpenAI API key to be configured in your `.env` file as `OPEN_AI_API_KEY`. The agent uses GPT-4o-mini model with conversation memory support and GPT Actions (function calling) to interact with all API endpoints.

#### POST `/api/agent/chat`

Chat with GPT-4o-mini agent with conversation memory and GPT Actions.

This endpoint allows you to have a conversation with an AI agent powered by GPT-4o-mini. The agent maintains conversation context through thread IDs, allowing for multi-turn conversations. **Most importantly, the agent can automatically call any of the API endpoints below using GPT Actions (function calling)**, making it capable of:

- Browsing restaurants and viewing menus
- Getting item details
- Building shopping carts
- Computing cost estimates
- Creating receipts for orders
- Creating and tracking DoorDash deliveries

The agent will automatically decide when to call API functions based on your requests, making it a powerful conversational interface to the entire DaNomNoms API.

**Request Body:**
```json
{
  "prompt": "Hello, what can you help me with?",
  "thread_id": "thread_abc123"
}
```

**Required Fields:**
- `prompt`: User prompt/question for the agent

**Optional Fields:**
- `thread_id`: Thread ID to continue a conversation. If not provided, a new thread will be created automatically.

**Response:**
```json
{
  "response": "Hello! I'm here to help you with various tasks. I can answer questions, provide information, help with problem-solving, and much more. What would you like to know?",
  "thread_id": "thread_abc123"
}
```

**Example - Start a new conversation:**
```bash
curl -X POST https://danomnoms-api.onrender.com/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Hello, what can you help me with?"
  }'
```

**Example - Continue a conversation:**
```bash
curl -X POST https://danomnoms-api.onrender.com/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What did I just ask you?",
    "thread_id": "thread_abc123"
  }'
```

**Example - Using GPT Actions (the agent calls API endpoints automatically):**

The agent can automatically call API endpoints based on your natural language requests:

```bash
# Agent will automatically call list_restaurants function
curl -X POST https://danomnoms-api.onrender.com/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What restaurants are available? Show me the first 5."
  }'

# Agent will call get_restaurant_menu function automatically
curl -X POST https://danomnoms-api.onrender.com/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Show me the menu for restaurant with ID 69347db4fa0aa2fde8fdaeb3",
    "thread_id": "thread_abc123"
  }'

# Agent can handle complex multi-step requests
curl -X POST https://danomnoms-api.onrender.com/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Find me a restaurant, show me its menu, and build a cart with 2 burgers",
    "thread_id": "thread_abc123"
  }'

# Agent can track deliveries
curl -X POST https://danomnoms-api.onrender.com/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Track the delivery status for delivery D-12345",
    "thread_id": "thread_abc123"
  }'
```

**Available GPT Actions (Functions):**

The agent has access to all of the following API endpoints as functions:

1. **`list_restaurants`** - List all restaurants with pagination (supports `limit` and `skip` parameters)
2. **`get_restaurant_menu`** - Get menu items for a specific restaurant
3. **`get_menu_item`** - Get details of a specific menu item by ID
4. **`build_cart`** - Build a shopping cart with items from a restaurant
5. **`compute_cost_estimate`** - Compute cost estimate for a cart without building the full cart
6. **`create_receipt`** - Create a receipt for a completed order
7. **`create_delivery`** - Create a new DoorDash delivery
8. **`track_delivery`** - Get the status of a DoorDash delivery by external delivery ID

The agent will automatically determine which functions to call and in what order based on your natural language requests.

**Notes:**
- Each conversation thread maintains its own memory and context
- Use the `thread_id` from the response to continue the same conversation
- If you don't provide a `thread_id`, a new conversation thread will be created
- Conversation history is stored in memory per thread and is used to maintain context across messages
- The agent uses GPT-4o-mini model with a temperature of 0.7 and maximum of 1000 tokens per response
- **GPT Actions**: The agent can automatically call API endpoints (functions) based on your requests, allowing for complex multi-step operations
- All API calls are made to `https://danomnoms-api.onrender.com` as the base URL
- The agent supports up to 10 iterations of function calls in a single conversation turn to handle complex workflows

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Error message describing what went wrong"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error message describing the server error"
}
```

---

## Additional Resources

- [API Documentation (ReDoc)](https://danomnoms-api.onrender.com/redoc) - Interactive API documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [DoorDash Developer Portal](https://developer.doordash.com/)
- [DoorDash Drive API Tutorial](https://developer.doordash.com/en-US/docs/drive/tutorials/get_started/)
