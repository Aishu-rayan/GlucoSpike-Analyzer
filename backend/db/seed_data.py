"""
Seed the database with initial GI data from the existing gi_database.py
"""

import asyncio
from datetime import datetime
from sqlalchemy import select
from .engine import async_session, init_db
from .models import Food, GIValue


# Import existing food database
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database.gi_database import FOOD_DATABASE


async def seed_foods_and_gi():
    """Seed the database with existing food data"""
    
    await init_db()
    
    async with async_session() as session:
        # Check if already seeded
        result = await session.execute(select(Food).limit(1))
        if result.scalar_one_or_none():
            print("Database already seeded, skipping...")
            return
        
        print(f"Seeding {len(FOOD_DATABASE)} foods...")
        
        for food_name, data in FOOD_DATABASE.items():
            # Create Food entry
            food = Food(
                canonical_name=food_name,
                carbs_per_100g=data.get("carbs"),
                protein_per_100g=data.get("protein"),
                fat_per_100g=data.get("fat"),
                fiber_per_100g=data.get("fiber"),
                serving_size_g=data.get("serving_size"),
                category=data.get("category"),
                data_source="manual",
            )
            session.add(food)
            await session.flush()  # Get the food.id
            
            # Create GI Value entry
            gi_value = GIValue(
                food_id=food.id,
                food_name=food_name,
                gi=data.get("gi", 50),  # Default to 50 if not specified
                gi_category=classify_gi(data.get("gi", 50)),
                source="Initial Database",
                source_url="https://glycemicindex.com/",
                confidence="medium",
            )
            session.add(gi_value)
        
        await session.commit()
        print("Database seeded successfully!")


def classify_gi(gi: float) -> str:
    """Classify GI value into category"""
    if gi <= 55:
        return "low"
    elif gi <= 69:
        return "medium"
    else:
        return "high"


if __name__ == "__main__":
    asyncio.run(seed_foods_and_gi())

