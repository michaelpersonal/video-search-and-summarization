import os
import json
from sqlalchemy.orm import Session
from database import SessionLocal, create_tables
from models import SparePart

def check_database():
    print("🔍 Checking database contents...")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Get all spare parts
        spare_parts = db.query(SparePart).all()
        
        print(f"📊 Found {len(spare_parts)} spare parts in database:")
        for part in spare_parts:
            print(f"  - {part.material_number}: {part.description}")
            if part.image_path:
                print(f"    Image: {part.image_path}")
        
        # Check if any parts have images
        parts_with_images = db.query(SparePart).filter(SparePart.image_path.isnot(None)).all()
        print(f"\n📸 Parts with images: {len(parts_with_images)}")
        
        # Check the mapping file
        mapping_file = os.path.join(os.path.dirname(__file__), "part_image_embeddings_map.json")
        if os.path.exists(mapping_file):
            with open(mapping_file, 'r') as f:
                mapping = json.load(f)
            
            print(f"\n🗂️ AI mapping contains {len(mapping)} entries:")
            for entry in mapping:
                print(f"  - {entry['material_number']}: {entry['image_path']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_database() 