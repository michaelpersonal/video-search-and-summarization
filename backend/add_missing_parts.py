import os
import json
import sqlite3

def add_missing_parts():
    print("🔧 Adding missing spare parts to database...")
    
    # Read the mapping file
    mapping_file = os.path.join(os.path.dirname(__file__), "part_image_embeddings_map.json")
    if not os.path.exists(mapping_file):
        print("❌ Mapping file not found")
        return
    
    with open(mapping_file, 'r') as f:
        mapping = json.load(f)
    
    # Connect to the database
    db_path = os.path.join(os.path.dirname(__file__), "spareparts.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check existing material numbers
        cursor.execute("SELECT material_number FROM spare_parts")
        existing_material_numbers = {row[0] for row in cursor.fetchall()}
        
        print(f"📊 Found {len(existing_material_numbers)} existing parts in database")
        
        # Add missing parts
        added_count = 0
        for entry in mapping:
            material_number = entry['material_number']
            
            if material_number not in existing_material_numbers:
                # Insert the new spare part
                cursor.execute("""
                    INSERT INTO spare_parts (material_number, description, category, manufacturer, specifications, image_path, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
                """, (
                    material_number,
                    entry['description'],
                    'AI Detected',
                    'Unknown',
                    'Detected by AI image analysis',
                    entry['image_path']
                ))
                added_count += 1
                print(f"✅ Added: {material_number}")
            else:
                print(f"⏭️ Skipped: {material_number} (already exists)")
        
        # Commit changes
        conn.commit()
        print(f"\n🎉 Successfully added {added_count} new spare parts to database")
        
        # Show final count
        cursor.execute("SELECT COUNT(*) FROM spare_parts")
        total_count = cursor.fetchone()[0]
        print(f"📊 Total spare parts in database: {total_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_missing_parts() 