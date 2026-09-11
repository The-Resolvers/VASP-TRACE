import asyncio
import json
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def seed_tags():
    """
    Ingest GraphSense TagPacks into MongoDB.
    """
    # Assuming default MongoDB local URI for script
    uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(uri)
    db = client["vasp_trace"]
    collection = db["vasp_tags"]
    
    tagpacks_path = "data/tagpacks.json"
    if not os.path.exists(tagpacks_path):
        print(f"Tagpacks file not found at {tagpacks_path}")
        return

    with open(tagpacks_path, "r") as f:
        try:
            data = json.load(f)
            # Depending on format, insert many
            # Expected format: list of dicts with 'address', 'label', 'actor'
            if isinstance(data, list) and len(data) > 0:
                # Create unique index on address for O(1) lookups
                await collection.create_index("address", unique=True)
                
                # Insert
                try:
                    await collection.insert_many(data, ordered=False)
                    print(f"Successfully seeded {len(data)} tags.")
                except Exception as e:
                    print(f"Error inserting (might be duplicates): {e}")
            else:
                print("No data or invalid format in tagpacks.json")
        except json.JSONDecodeError:
            print(f"Failed to parse JSON from {tagpacks_path}")

    client.close()

if __name__ == "__main__":
    asyncio.run(seed_tags())
