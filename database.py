"""
Database service module for MongoDB operations.
"""
from typing import List, Dict, Any, Optional
from pymongo.mongo_client import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from mongo import get_mongodb_client, get_mongodb_database, RESTAURANTS_COLLECTION, ITEMS_COLLECTION


class DatabaseService:
    """Service class for database operations."""
    
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self._connect()
    
    def _connect(self):
        """Establish MongoDB connection."""
        self.client = get_mongodb_client()
        self.db = get_mongodb_database(self.client)
    
    def get_restaurants_collection(self) -> Collection:
        """Get restaurants collection."""
        return self.db[RESTAURANTS_COLLECTION]
    
    def get_items_collection(self) -> Collection:
        """Get items collection."""
        return self.db[ITEMS_COLLECTION]
    
    def list_restaurants(self, limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
        """
        List all restaurants with pagination.
        
        Args:
            limit: Maximum number of restaurants to return
            skip: Number of restaurants to skip
            
        Returns:
            List of restaurant documents
        """
        restaurants_col = self.get_restaurants_collection()
        restaurants = list(restaurants_col.find({}).limit(limit).skip(skip))
        
        # Convert ObjectId to string for JSON serialization
        for restaurant in restaurants:
            restaurant['_id'] = str(restaurant['_id'])
            if 'items' in restaurant:
                restaurant['items'] = [str(item_id) for item_id in restaurant['items']]
        
        return restaurants
    
    def get_restaurant_by_id(self, restaurant_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a restaurant by MongoDB _id.
        
        Args:
            restaurant_id: MongoDB _id of the restaurant
            
        Returns:
            Restaurant document or None if not found
        """
        from bson import ObjectId
        restaurants_col = self.get_restaurants_collection()
        
        try:
            restaurant = restaurants_col.find_one({'_id': ObjectId(restaurant_id)})
            if restaurant:
                restaurant['_id'] = str(restaurant['_id'])
                if 'items' in restaurant:
                    restaurant['items'] = [str(item_id) for item_id in restaurant['items']]
            return restaurant
        except Exception:
            return None
    
    def get_restaurant_by_store_id(self, store_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a restaurant by store_id.
        
        Args:
            store_id: Store ID of the restaurant
            
        Returns:
            Restaurant document or None if not found
        """
        restaurants_col = self.get_restaurants_collection()
        restaurant = restaurants_col.find_one({'store_id': store_id})
        
        if restaurant:
            restaurant['_id'] = str(restaurant['_id'])
            if 'items' in restaurant:
                restaurant['items'] = [str(item_id) for item_id in restaurant['items']]
        
        return restaurant
    
    def get_menu_items(self, restaurant_id: str) -> List[Dict[str, Any]]:
        """
        Get menu items for a restaurant by restaurant MongoDB _id.
        
        Args:
            restaurant_id: MongoDB _id of the restaurant
            
        Returns:
            List of menu item documents
        """
        from bson import ObjectId
        restaurants_col = self.get_restaurants_collection()
        items_col = self.get_items_collection()
        
        try:
            restaurant = restaurants_col.find_one({'_id': ObjectId(restaurant_id)})
            if not restaurant:
                return []
            
            # Get items using the items array in restaurant document
            item_ids = restaurant.get('items', [])
            if not item_ids:
                # Fallback: query by store_id if items array is empty
                store_id = restaurant.get('store_id')
                if store_id:
                    items = list(items_col.find({'store_id': store_id}))
                else:
                    items = []
            else:
                items = list(items_col.find({'_id': {'$in': item_ids}}))
            
            # Convert ObjectId to string
            for item in items:
                item['_id'] = str(item['_id'])
            
            return items
        except Exception:
            return []
    
    def get_menu_items_by_store_id(self, store_id: str) -> List[Dict[str, Any]]:
        """
        Get menu items for a restaurant by store_id.
        
        Args:
            store_id: Store ID of the restaurant
            
        Returns:
            List of menu item documents
        """
        items_col = self.get_items_collection()
        items = list(items_col.find({'store_id': store_id}))
        
        # Convert ObjectId to string
        for item in items:
            item['_id'] = str(item['_id'])
        
        return items
    
    def get_item_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a menu item by MongoDB _id.
        
        Args:
            item_id: MongoDB _id of the menu item
            
        Returns:
            Menu item document or None if not found
        """
        from bson import ObjectId
        items_col = self.get_items_collection()
        
        try:
            item = items_col.find_one({'_id': ObjectId(item_id)})
            if item:
                item['_id'] = str(item['_id'])
            return item
        except Exception:
            return None
    
    def get_items_by_ids(self, item_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get menu items by their MongoDB _ids.
        
        Args:
            item_ids: List of MongoDB _id strings
            
        Returns:
            List of menu item documents
        """
        from bson import ObjectId
        items_col = self.get_items_collection()
        
        try:
            object_ids = [ObjectId(item_id) for item_id in item_ids]
            items = list(items_col.find({'_id': {'$in': object_ids}}))
            
            # Convert ObjectId to string
            for item in items:
                item['_id'] = str(item['_id'])
            
            return items
        except Exception:
            return []
    
    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()


# Global database service instance
db_service = DatabaseService()

