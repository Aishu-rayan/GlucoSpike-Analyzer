"""
GI Data Import Script

Imports Glycemic Index data from CSV files into the database.
Supports multiple sources with confidence levels.

CSV Format:
food_name,gi,source,source_url,confidence,notes

Usage:
    python -m scripts.import_gi_csv data/gi_data.csv
"""

import asyncio
import csv
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from db.engine import async_session, init_db
from db.models import Food, GIValue


def classify_gi(gi: float) -> str:
    """Classify GI value into category"""
    if gi <= 55:
        return "low"
    elif gi <= 69:
        return "medium"
    else:
        return "high"


async def import_gi_csv(csv_path: str, source_name: str = None, default_confidence: str = "medium"):
    """
    Import GI data from a CSV file.
    
    Args:
        csv_path: Path to CSV file
        source_name: Override source name for all entries
        default_confidence: Default confidence level if not in CSV
    """
    await init_db()
    
    csv_file = Path(csv_path)
    if not csv_file.exists():
        print(f"Error: File not found: {csv_path}")
        return
    
    print(f"Importing GI data from {csv_path}...")
    
    imported = 0
    updated = 0
    skipped = 0
    
    async with async_session() as session:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                food_name = row.get('food_name', '').strip().lower()
                if not food_name:
                    skipped += 1
                    continue
                
                try:
                    gi = float(row.get('gi', 0))
                except ValueError:
                    print(f"  Skipping {food_name}: invalid GI value")
                    skipped += 1
                    continue
                
                if gi <= 0 or gi > 150:
                    print(f"  Skipping {food_name}: GI {gi} out of range")
                    skipped += 1
                    continue
                
                source = source_name or row.get('source', 'Imported')
                source_url = row.get('source_url', '')
                confidence = row.get('confidence', default_confidence)
                notes = row.get('notes', '')
                
                # Check if food exists
                food_result = await session.execute(
                    select(Food).where(Food.canonical_name == food_name)
                )
                food = food_result.scalar_one_or_none()
                
                # Check if GI value already exists for this source
                existing_gi = await session.execute(
                    select(GIValue).where(
                        GIValue.food_name == food_name,
                        GIValue.source == source
                    )
                )
                existing = existing_gi.scalar_one_or_none()
                
                if existing:
                    # Update existing
                    existing.gi = gi
                    existing.gi_category = classify_gi(gi)
                    existing.source_url = source_url or existing.source_url
                    existing.confidence = confidence
                    existing.notes = notes or existing.notes
                    existing.updated_at = datetime.utcnow()
                    updated += 1
                else:
                    # Create new
                    gi_value = GIValue(
                        food_id=food.id if food else None,
                        food_name=food_name,
                        gi=gi,
                        gi_category=classify_gi(gi),
                        source=source,
                        source_url=source_url,
                        confidence=confidence,
                        notes=notes,
                    )
                    session.add(gi_value)
                    imported += 1
                
                # Create food entry if it doesn't exist
                if not food:
                    new_food = Food(
                        canonical_name=food_name,
                        data_source="gi_import",
                    )
                    session.add(new_food)
        
        await session.commit()
    
    print(f"\nImport complete!")
    print(f"  Imported: {imported}")
    print(f"  Updated: {updated}")
    print(f"  Skipped: {skipped}")


async def create_sample_csv():
    """Create a sample CSV file with GI data format"""
    sample_data = [
        {"food_name": "white rice", "gi": 73, "source": "University of Sydney", "source_url": "https://glycemicindex.com", "confidence": "high", "notes": "Boiled, white"},
        {"food_name": "brown rice", "gi": 50, "source": "University of Sydney", "source_url": "https://glycemicindex.com", "confidence": "high", "notes": "Boiled"},
        {"food_name": "apple", "gi": 36, "source": "University of Sydney", "source_url": "https://glycemicindex.com", "confidence": "high", "notes": "Raw, with skin"},
        {"food_name": "banana", "gi": 51, "source": "University of Sydney", "source_url": "https://glycemicindex.com", "confidence": "high", "notes": "Ripe"},
        {"food_name": "white bread", "gi": 75, "source": "University of Sydney", "source_url": "https://glycemicindex.com", "confidence": "high", "notes": ""},
        {"food_name": "whole wheat bread", "gi": 54, "source": "University of Sydney", "source_url": "https://glycemicindex.com", "confidence": "high", "notes": ""},
        {"food_name": "potato", "gi": 78, "source": "University of Sydney", "source_url": "https://glycemicindex.com", "confidence": "high", "notes": "Boiled"},
        {"food_name": "sweet potato", "gi": 63, "source": "University of Sydney", "source_url": "https://glycemicindex.com", "confidence": "high", "notes": "Boiled"},
        {"food_name": "oatmeal", "gi": 55, "source": "Harvard Health", "source_url": "https://health.harvard.edu", "confidence": "high", "notes": "Rolled oats"},
        {"food_name": "lentils", "gi": 32, "source": "University of Sydney", "source_url": "https://glycemicindex.com", "confidence": "high", "notes": "Boiled"},
    ]
    
    output_path = Path(__file__).parent.parent / "data" / "sample_gi_data.csv"
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["food_name", "gi", "source", "source_url", "confidence", "notes"])
        writer.writeheader()
        writer.writerows(sample_data)
    
    print(f"Sample CSV created at: {output_path}")


async def export_current_gi_data():
    """Export current GI data from database to CSV"""
    await init_db()
    
    output_path = Path(__file__).parent.parent / "data" / "exported_gi_data.csv"
    output_path.parent.mkdir(exist_ok=True)
    
    async with async_session() as session:
        result = await session.execute(select(GIValue))
        gi_values = result.scalars().all()
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["food_name", "gi", "source", "source_url", "confidence", "notes"])
            writer.writeheader()
            
            for gi in gi_values:
                writer.writerow({
                    "food_name": gi.food_name,
                    "gi": gi.gi,
                    "source": gi.source,
                    "source_url": gi.source_url or "",
                    "confidence": gi.confidence,
                    "notes": gi.notes or "",
                })
    
    print(f"Exported {len(gi_values)} GI values to: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m scripts.import_gi_csv <csv_path>  - Import GI data from CSV")
        print("  python -m scripts.import_gi_csv --sample    - Create sample CSV")
        print("  python -m scripts.import_gi_csv --export    - Export current GI data")
        sys.exit(1)
    
    arg = sys.argv[1]
    
    if arg == "--sample":
        asyncio.run(create_sample_csv())
    elif arg == "--export":
        asyncio.run(export_current_gi_data())
    else:
        source = sys.argv[2] if len(sys.argv) > 2 else None
        asyncio.run(import_gi_csv(arg, source))

