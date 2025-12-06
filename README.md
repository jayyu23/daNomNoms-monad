# daNomNoms-monad

Monad x402 SF Hackathon Project

A REST API for the DaNomNoms food delivery service, integrating with DoorDash for delivery fulfillment.

## Table of Contents

- [Setup](#setup)
- [Environment Variables](#environment-variables)
- [Running the Server](#running-the-server)
- [API Documentation](#api-documentation)
  - [General Endpoints](#general-endpoints)
  - [Restaurant Endpoints](#restaurant-endpoints)
  - [DoorDash Delivery Endpoints](#doordash-delivery-endpoints)

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

The API will be available at `http://localhost:8000`

Interactive API documentation (Swagger UI) is available at `http://localhost:8000/docs`
Alternative API documentation (ReDoc) is available at `http://localhost:8000/redoc`

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# MongoDB connection string
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority

# DoorDash API credentials
DOORDASH_DEVELOPER_ID=your_developer_id
DOORDASH_KEY_ID=your_key_id
DOORDASH_SIGNING_SECRET=your_signing_secret
```

**MongoDB Setup:**
- Get a free MongoDB database from [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- Create a cluster and get your connection string
- Replace `username`, `password`, and `cluster` with your actual values

**DoorDash Credentials:**
- Get your DoorDash credentials from the [DoorDash Developer Portal](https://developer.doordash.com/)
- The `DOORDASH_SIGNING_SECRET` should be base64url encoded

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

5. **Click "Create Web Service"** and wait for deployment

### Post-Deployment

1. **Update CORS settings** in `app.py`:
   - Change `allow_origins=["*"]` to your frontend domain(s)
   - Example: `allow_origins=["https://your-frontend.vercel.app"]`

2. **Access your API:**
   - Your API will be available at: `https://your-service-name.onrender.com`
   - API docs: `https://your-service-name.onrender.com/docs`
   - Health check: `https://your-service-name.onrender.com/health`

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

Base URL: `http://localhost:8000`

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
    "get_menu": "GET /api/restaurants/{restaurant_id}/menu",
    "get_item": "GET /api/restaurants/items/{item_id}",
    "build_cart": "POST /api/restaurants/cart",
    "compute_cost_estimate": "POST /api/restaurants/cost-estimate",
    "create_delivery": "POST /api/doordash/deliveries",
    "track_delivery": "GET /api/doordash/deliveries/{external_delivery_id}"
  }
}
```

**Example:**
```bash
curl http://localhost:8000/
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
curl http://localhost:8000/health
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
curl "http://localhost:8000/api/restaurants/?limit=10&skip=0"
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
curl "http://localhost:8000/api/restaurants/69347db4fa0aa2fde8fdaeb3/menu"
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
curl "http://localhost:8000/api/restaurants/items/69347db5fa0aa2fde8fdaf17"
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
curl -X POST http://localhost:8000/api/restaurants/cart \
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
curl -X POST http://localhost:8000/api/doordash/deliveries \
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
curl "http://localhost:8000/api/doordash/deliveries/D-12345"
```

**Delivery Status Values:**
- `created`: Delivery has been created
- `enroute_to_pickup`: Dasher is on the way to pick up the order
- `delivery_confirmed`: Delivery has been confirmed
- `enroute_to_dropoff`: Dasher is on the way to drop off the order
- `delivered`: Delivery has been completed

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

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [DoorDash Developer Portal](https://developer.doordash.com/)
- [DoorDash Drive API Tutorial](https://developer.doordash.com/en-US/docs/drive/tutorials/get_started/)
