
import os
import sqlite3
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import BulkWriteError, DuplicateKeyError
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MongoDB connection configuration
MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    raise ValueError("MONGODB_URI not found in environment variables. Please check your .env file.")
    
DATABASE_NAME = "DaNomNoms"
RESTAURANTS_COLLECTION = "Restaurants"
ITEMS_COLLECTION = "Items"
RECEIPTS_COLLECTION = "Receipts"
SQLITE_DB_PATH = "doordash_data.db"


def get_mongodb_client() -> MongoClient:
    """
    Creates and returns a MongoDB client with proper connection settings.
    
    Returns:
        MongoClient: Configured MongoDB client instance
    """
    client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))
    return client


def get_mongodb_database(client: MongoClient):
    """
    Gets the DaNomNoms database from the MongoDB client.
    
    Args:
        client: MongoDB client instance
        
    Returns:
        Database: DaNomNoms database instance
    """
    return client[DATABASE_NAME]


def verify_mongodb_connection(client: MongoClient) -> bool:
    """
    Verifies the MongoDB connection by sending a ping.
    
    Args:
        client: MongoDB client instance
        
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        client.admin.command('ping')
        return True
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        return False


def check_migration_already_done(db) -> bool:
    """
    Checks if the migration has already been performed by checking if collections exist and have data.
    
    Args:
        db: MongoDB database instance
        
    Returns:
        bool: True if migration appears to have been done, False otherwise
    """
    restaurants_col = db[RESTAURANTS_COLLECTION]
    items_col = db[ITEMS_COLLECTION]
    
    restaurant_count = restaurants_col.count_documents({})
    item_count = items_col.count_documents({})
    
    if restaurant_count > 0 or item_count > 0:
        print(f"Warning: Migration may have already been done. Found {restaurant_count} restaurants and {item_count} items.")
        return True
    return False


def read_restaurants_from_sqlite(db_path: str) -> List[Dict[str, Any]]:
    """
    Reads all restaurants from the SQLite database.
    
    Args:
        db_path: Path to the SQLite database file
        
    Returns:
        List of restaurant dictionaries
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, store_id, name, description, delivery_fee, eta, 
               average_rating, number_of_ratings, price_range, distance_miles, 
               link, created_at, address, operating_hours
        FROM restaurants
        ORDER BY id
    """)
    
    restaurants = []
    for row in cursor.fetchall():
        restaurant = {
            'sqlite_id': row['id'],
            'store_id': row['store_id'],
            'name': row['name'],
            'description': row['description'],
            'delivery_fee': row['delivery_fee'],
            'eta': row['eta'],
            'average_rating': row['average_rating'],
            'number_of_ratings': row['number_of_ratings'],
            'price_range': row['price_range'],
            'distance_miles': row['distance_miles'],
            'link': row['link'],
            'created_at': row['created_at'],
            'address': row['address'],
            'operating_hours': row['operating_hours']
        }
        restaurants.append(restaurant)
    
    conn.close()
    return restaurants


def read_menu_items_from_sqlite(db_path: str) -> List[Dict[str, Any]]:
    """
    Reads all menu items from the SQLite database.
    
    Args:
        db_path: Path to the SQLite database file
        
    Returns:
        List of menu item dictionaries
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, restaurant_id, store_id, name, description, price, 
               rating_percent, review_count, image_url, created_at
        FROM menu_items
        ORDER BY id
    """)
    
    items = []
    for row in cursor.fetchall():
        item = {
            'sqlite_id': row['id'],
            'restaurant_id': row['restaurant_id'],
            'store_id': row['store_id'],
            'name': row['name'],
            'description': row['description'],
            'price': row['price'],
            'rating_percent': row['rating_percent'],
            'review_count': row['review_count'],
            'image_url': row['image_url'],
            'created_at': row['created_at']
        }
        items.append(item)
    
    conn.close()
    return items


def create_indexes(db):
    """
    Creates necessary indexes on MongoDB collections for better query performance.
    
    Args:
        db: MongoDB database instance
    """
    restaurants_col = db[RESTAURANTS_COLLECTION]
    items_col = db[ITEMS_COLLECTION]
    
    # Create indexes
    restaurants_col.create_index("store_id", unique=True)
    restaurants_col.create_index("sqlite_id")
    items_col.create_index("store_id")
    items_col.create_index("restaurant_id")
    items_col.create_index("sqlite_id")
    
    print("Indexes created successfully.")


def one_time_migrate_sqlite_to_mongodb(force: bool = False) -> bool:
    """
    ONE-TIME MIGRATION FUNCTION: Migrates data from SQLite to MongoDB.
    
    This function should only be run once. It reads all restaurants and menu items
    from the SQLite database and inserts them into MongoDB collections.
    
    Args:
        force: If True, proceed even if migration appears to have been done
        
    Returns:
        bool: True if migration was successful, False otherwise
    """
    print("=" * 60)
    print("ONE-TIME MIGRATION: SQLite to MongoDB")
    print("=" * 60)
    
    # Connect to MongoDB
    print("\n1. Connecting to MongoDB...")
    client = get_mongodb_client()
    
    if not verify_mongodb_connection(client):
        print("Failed to connect to MongoDB. Aborting migration.")
        return False
    
    print("✓ MongoDB connection verified.")
    
    db = get_mongodb_database(client)
    
    # Check if migration already done
    if not force and check_migration_already_done(db):
        response = input("\nMigration may have already been done. Continue anyway? (yes/no): ")
        if response.lower() != 'yes':
            print("Migration aborted.")
            client.close()
            return False
    
    # Read data from SQLite
    print("\n2. Reading data from SQLite database...")
    try:
        restaurants = read_restaurants_from_sqlite(SQLITE_DB_PATH)
        menu_items = read_menu_items_from_sqlite(SQLITE_DB_PATH)
        print(f"✓ Read {len(restaurants)} restaurants and {len(menu_items)} menu items from SQLite.")
    except Exception as e:
        print(f"✗ Error reading from SQLite: {e}")
        client.close()
        return False
    
    # Create indexes before inserting data
    print("\n3. Creating indexes...")
    try:
        create_indexes(db)
    except Exception as e:
        print(f"Warning: Error creating indexes: {e}")
    
    # Insert restaurants
    print("\n4. Inserting restaurants into MongoDB...")
    restaurants_col = db[RESTAURANTS_COLLECTION]
    
    try:
        # Use bulk operations for efficiency
        restaurant_docs = []
        for restaurant in restaurants:
            # Remove None values to keep documents clean
            restaurant_doc = {k: v for k, v in restaurant.items() if v is not None}
            restaurant_docs.append(restaurant_doc)
        
        if restaurant_docs:
            result = restaurants_col.insert_many(restaurant_docs, ordered=False)
            print(f"✓ Successfully inserted {len(result.inserted_ids)} restaurants.")
        else:
            print("⚠ No restaurants to insert.")
    except BulkWriteError as e:
        inserted = len(e.details.get('writeErrors', []))
        print(f"⚠ Some restaurants may have duplicates. Checked {len(restaurant_docs)} restaurants.")
        if inserted > 0:
            print(f"✓ Inserted {inserted} restaurants.")
    except Exception as e:
        print(f"✗ Error inserting restaurants: {e}")
        client.close()
        return False
    
    # Insert menu items
    print("\n5. Inserting menu items into MongoDB...")
    items_col = db[ITEMS_COLLECTION]
    
    try:
        # Use bulk operations for efficiency
        item_docs = []
        for item in menu_items:
            # Remove None values to keep documents clean
            item_doc = {k: v for k, v in item.items() if v is not None}
            item_docs.append(item_doc)
        
        if item_docs:
            # Insert in batches to handle large datasets
            batch_size = 1000
            total_inserted = 0
            
            for i in range(0, len(item_docs), batch_size):
                batch = item_docs[i:i + batch_size]
                try:
                    result = items_col.insert_many(batch, ordered=False)
                    total_inserted += len(result.inserted_ids)
                    print(f"  Inserted batch {i//batch_size + 1}: {len(result.inserted_ids)} items")
                except BulkWriteError as e:
                    # Count successful inserts
                    successful = len(batch) - len(e.details.get('writeErrors', []))
                    total_inserted += successful
                    print(f"  Batch {i//batch_size + 1}: {successful} items inserted (some duplicates skipped)")
            
            print(f"✓ Successfully inserted {total_inserted} menu items.")
        else:
            print("⚠ No menu items to insert.")
    except Exception as e:
        print(f"✗ Error inserting menu items: {e}")
        client.close()
        return False
    
    # Verify data consistency
    print("\n6. Verifying data consistency...")
    final_restaurant_count = restaurants_col.count_documents({})
    final_item_count = items_col.count_documents({})
    
    print(f"✓ MongoDB now contains:")
    print(f"  - {final_restaurant_count} restaurants")
    print(f"  - {final_item_count} menu items")
    
    # Verify relationships
    print("\n7. Verifying data relationships...")
    sample_restaurant = restaurants_col.find_one({})
    if sample_restaurant:
        sample_store_id = sample_restaurant.get('store_id')
        items_for_restaurant = items_col.count_documents({'store_id': sample_store_id})
        print(f"✓ Sample verification: Restaurant '{sample_restaurant.get('name')}' has {items_for_restaurant} items")
    
    client.close()
    
    print("\n" + "=" * 60)
    print("MIGRATION COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    return True


def get_restaurant_item_relationships_from_sqlite(db_path: str) -> Dict[int, List[int]]:
    """
    Reads restaurant-item relationships from SQLite database.
    
    Args:
        db_path: Path to the SQLite database file
        
    Returns:
        Dictionary mapping restaurant SQLite ID to list of item SQLite IDs
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT restaurant_id, id as item_id
        FROM menu_items
        WHERE restaurant_id IS NOT NULL
        ORDER BY restaurant_id, id
    """)
    
    relationships = {}
    for row in cursor.fetchall():
        restaurant_id = row[0]
        item_id = row[1]
        
        if restaurant_id not in relationships:
            relationships[restaurant_id] = []
        relationships[restaurant_id].append(item_id)
    
    conn.close()
    return relationships


def one_time_associate_items_with_restaurants(force: bool = False) -> bool:
    """
    ONE-TIME MIGRATION FUNCTION: Associates items with restaurants.
    
    This function updates each restaurant document in MongoDB to include an 'items' field
    that contains the MongoDB _id values of all items that belong to that restaurant.
    The relationships are based on the restaurant_id field in the SQLite database.
    
    Args:
        force: If True, proceed even if items field already exists
        
    Returns:
        bool: True if migration was successful, False otherwise
    """
    print("=" * 60)
    print("ONE-TIME MIGRATION: Associate Items with Restaurants")
    print("=" * 60)
    
    # Connect to MongoDB
    print("\n1. Connecting to MongoDB...")
    client = get_mongodb_client()
    
    if not verify_mongodb_connection(client):
        print("Failed to connect to MongoDB. Aborting migration.")
        return False
    
    print("✓ MongoDB connection verified.")
    
    db = get_mongodb_database(client)
    restaurants_col = db[RESTAURANTS_COLLECTION]
    items_col = db[ITEMS_COLLECTION]
    
    # Check if restaurants and items exist
    restaurant_count = restaurants_col.count_documents({})
    item_count = items_col.count_documents({})
    
    if restaurant_count == 0:
        print("✗ No restaurants found in MongoDB. Please run the initial migration first.")
        client.close()
        return False
    
    if item_count == 0:
        print("✗ No items found in MongoDB. Please run the initial migration first.")
        client.close()
        return False
    
    print(f"✓ Found {restaurant_count} restaurants and {item_count} items in MongoDB.")
    
    # Check if migration already done
    restaurants_with_items = restaurants_col.count_documents({"items": {"$exists": True, "$ne": []}})
    if not force and restaurants_with_items > 0:
        response = input(f"\nFound {restaurants_with_items} restaurants with items field. Continue anyway? (yes/no): ")
        if response.lower() != 'yes':
            print("Migration aborted.")
            client.close()
            return False
    
    # Read relationships from SQLite
    print("\n2. Reading restaurant-item relationships from SQLite...")
    try:
        relationships = get_restaurant_item_relationships_from_sqlite(SQLITE_DB_PATH)
        total_relationships = sum(len(items) for items in relationships.values())
        print(f"✓ Found {len(relationships)} restaurants with {total_relationships} item relationships in SQLite.")
    except Exception as e:
        print(f"✗ Error reading from SQLite: {e}")
        client.close()
        return False
    
    # Create a mapping from item SQLite ID to MongoDB _id
    print("\n3. Creating item ID mapping...")
    try:
        all_items = list(items_col.find({}, {"_id": 1, "sqlite_id": 1}))
        item_sqlite_to_mongo = {item["sqlite_id"]: item["_id"] for item in all_items if "sqlite_id" in item}
        print(f"✓ Mapped {len(item_sqlite_to_mongo)} items.")
    except Exception as e:
        print(f"✗ Error creating item mapping: {e}")
        client.close()
        return False
    
    # Update restaurants with items field
    print("\n4. Updating restaurants with items field...")
    try:
        all_restaurants = list(restaurants_col.find({}, {"_id": 1, "sqlite_id": 1, "name": 1}))
        updated_count = 0
        skipped_count = 0
        error_count = 0
        
        for restaurant in all_restaurants:
            restaurant_sqlite_id = restaurant.get("sqlite_id")
            
            if restaurant_sqlite_id is None:
                skipped_count += 1
                continue
            
            # Get item SQLite IDs for this restaurant
            item_sqlite_ids = relationships.get(restaurant_sqlite_id, [])
            
            # Convert to MongoDB _ids
            item_mongo_ids = []
            for item_sqlite_id in item_sqlite_ids:
                if item_sqlite_id in item_sqlite_to_mongo:
                    item_mongo_ids.append(item_sqlite_to_mongo[item_sqlite_id])
            
            # Update the restaurant document
            try:
                result = restaurants_col.update_one(
                    {"_id": restaurant["_id"]},
                    {"$set": {"items": item_mongo_ids}}
                )
                
                if result.modified_count > 0:
                    updated_count += 1
                    if updated_count % 10 == 0:
                        print(f"  Updated {updated_count} restaurants...")
            except Exception as e:
                error_count += 1
                print(f"  ⚠ Error updating restaurant {restaurant.get('name', 'unknown')}: {e}")
        
        print(f"✓ Updated {updated_count} restaurants with items field.")
        if skipped_count > 0:
            print(f"  ⚠ Skipped {skipped_count} restaurants (missing sqlite_id).")
        if error_count > 0:
            print(f"  ⚠ Errors updating {error_count} restaurants.")
            
    except Exception as e:
        print(f"✗ Error updating restaurants: {e}")
        client.close()
        return False
    
    # Verify data consistency
    print("\n5. Verifying data consistency...")
    try:
        # Check a few sample restaurants
        sample_restaurants = list(restaurants_col.find({"items": {"$exists": True, "$ne": []}}).limit(5))
        
        print(f"✓ Verification results:")
        for restaurant in sample_restaurants:
            items_count = len(restaurant.get("items", []))
            restaurant_name = restaurant.get("name", "Unknown")
            sqlite_id = restaurant.get("sqlite_id", "N/A")
            
            # Verify against SQLite
            expected_count = len(relationships.get(sqlite_id, [])) if isinstance(sqlite_id, int) else 0
            status = "✓" if items_count == expected_count else "⚠"
            print(f"  {status} {restaurant_name} (SQLite ID: {sqlite_id}): {items_count} items (expected: {expected_count})")
        
        # Overall statistics
        restaurants_with_items = restaurants_col.count_documents({"items": {"$exists": True, "$ne": []}})
        restaurants_without_items = restaurants_col.count_documents({"items": {"$exists": False}})
        restaurants_with_empty_items = restaurants_col.count_documents({"items": {"$exists": True, "$eq": []}})
        
        total_items_result = list(restaurants_col.aggregate([
            {"$match": {"items": {"$exists": True}}},
            {"$project": {"count": {"$size": "$items"}}},
            {"$group": {"_id": None, "total": {"$sum": "$count"}}}
        ]))
        total_items_count = total_items_result[0]["total"] if total_items_result else 0
        
        print(f"\n✓ Summary:")
        print(f"  - Restaurants with items: {restaurants_with_items}")
        print(f"  - Restaurants without items field: {restaurants_without_items}")
        print(f"  - Restaurants with empty items array: {restaurants_with_empty_items}")
        print(f"  - Total item references: {total_items_count}")
        
    except Exception as e:
        print(f"⚠ Warning: Error during verification: {e}")
    
    client.close()
    
    print("\n" + "=" * 60)
    print("MIGRATION COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    return True


if __name__ == '__main__':
    import sys
    
    print('Starting connection to MongoDB...')
    
    client = get_mongodb_client()
    
    # Send a ping to confirm a successful connection
    if verify_mongodb_connection(client):
        print("Pinged your deployment. You successfully connected to MongoDB!")
        
        # # Check if migration should be run
        # if len(sys.argv) > 1:
        #     force = '--force' in sys.argv
            
        #     if sys.argv[1] == '--migrate':
        #         print("\n" + "=" * 60)
        #         print("Running one-time migration...")
        #         print("=" * 60)
        #         success = one_time_migrate_sqlite_to_mongodb(force=force)
        #         sys.exit(0 if success else 1)
        #     elif sys.argv[1] == '--associate-items':
        #         print("\n" + "=" * 60)
        #         print("Running one-time item association migration...")
        #         print("=" * 60)
        #         success = one_time_associate_items_with_restaurants(force=force)
        #         sys.exit(0 if success else 1)
        #     else:
        #         print("\n" + "=" * 60)
        #         print("Available commands:")
        #         print("  python mongo.py --migrate")
        #         print("  python mongo.py --migrate --force  (to skip duplicate check)")
        #         print("  python mongo.py --associate-items")
        #         print("  python mongo.py --associate-items --force  (to skip duplicate check)")
        #         print("=" * 60)
        # else:
        #     print("\n" + "=" * 60)
        #     print("Available commands:")
        #     print("  python mongo.py --migrate")
        #     print("  python mongo.py --migrate --force  (to skip duplicate check)")
        #     print("  python mongo.py --associate-items")
        #     print("  python mongo.py --associate-items --force  (to skip duplicate check)")
        #     print("=" * 60)
    else:
        print("Failed to connect to MongoDB.")
    
    client.close()
