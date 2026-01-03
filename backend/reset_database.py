import os
from sqlalchemy import text
from database import SessionLocal, create_tables
from models import SparePart
from sample_data import create_sample_data

def reset_database():
    """Reset the database and recreate with sample data"""
    db = SessionLocal()
    
    try:
        # Drop all tables
        print("Dropping existing tables...")
        db.execute(text("DROP TABLE IF EXISTS spare_parts"))
        db.commit()
        print("✅ Tables dropped successfully")
        
        # Recreate tables
        print("Creating new tables...")
        create_tables()
        print("✅ Tables created successfully")
        
        # Create sample data
        print("Creating sample data...")
        create_sample_data()
        print("✅ Sample data created successfully")
        
        # Verify data
        count = db.query(SparePart).count()
        print(f"✅ Database now contains {count} spare parts")
        
        # Show sample data with image paths
        spare_parts = db.query(SparePart).all()
        print("\nSample spare parts with image paths:")
        for part in spare_parts:
            print(f"  {part.material_number}: {part.description}")
            if part.image_path:
                print(f"    Image: {part.image_path}")
            else:
                print(f"    Image: None")
        
    except Exception as e:
        print(f"❌ Error resetting database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_database() 