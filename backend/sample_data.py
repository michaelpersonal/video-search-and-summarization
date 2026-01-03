from sqlalchemy.orm import Session
from database import SessionLocal, create_tables
from models import SparePart

def create_sample_data():
    """Create sample spare parts data"""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_count = db.query(SparePart).count()
        if existing_count > 0:
            print(f"Database already contains {existing_count} spare parts. Skipping sample data creation.")
            return
        
        sample_parts = [
            {
                "material_number": "SP001",
                "description": "Hydraulic Pump Seal Kit",
                "category": "Hydraulics",
                "manufacturer": "Parker Hannifin",
                "specifications": "High-pressure hydraulic seal kit for industrial pumps. Compatible with Parker P1 series pumps. Temperature range: -40°C to +120°C. Pressure rating: 350 bar.",
                "image_path": "images/1/IMG_3706.jpg"
            },
            {
                "material_number": "SP002",
                "description": "Bearing Assembly - Deep Groove Ball Bearing",
                "category": "Bearings",
                "manufacturer": "SKF",
                "specifications": "6205-2RS deep groove ball bearing. Bore: 25mm, OD: 52mm, Width: 15mm. Sealed on both sides. Load capacity: 14.0 kN dynamic, 7.8 kN static.",
                "image_path": "images/2/IMG_3705.jpg"
            },
            {
                "material_number": "SP003",
                "description": "Motor Coupling - Flexible Coupling",
                "category": "Power Transmission",
                "manufacturer": "Lovejoy",
                "specifications": "L-type flexible coupling. Bore sizes: 1/2\" to 1-1/4\". Torque capacity: 1,800 in-lbs. Material: Cast iron with rubber spider. For motor-to-pump applications.",
                "image_path": "images/3/IMG_3704.jpg"
            },
            {
                "material_number": "SP004",
                "description": "Filter Element - Air Filter",
                "category": "Filtration",
                "manufacturer": "Donaldson",
                "specifications": "P181017 air filter element. Efficiency: 99.9% at 10 microns. Flow rate: 200 CFM. Operating temperature: -40°F to +185°F. For industrial air compressors.",
                "image_path": "images/4/IMG_3703.jpg"
            },
            {
                "material_number": "SP005",
                "description": "Valve - Solenoid Valve",
                "category": "Valves",
                "manufacturer": "ASCO",
                "specifications": "2-way normally closed solenoid valve. Port size: 1/2\" NPT. Voltage: 24V DC. Pressure range: 0-150 PSI. Body material: Brass. For pneumatic systems.",
                "image_path": "images/5/IMG_3702.jpg"
            },
            {
                "material_number": "SP006",
                "description": "Gear - Spur Gear",
                "category": "Gears",
                "manufacturer": "Martin Sprocket",
                "specifications": "20-tooth spur gear. Module: 2.5. Bore: 20mm. Material: 1045 steel. Heat treated to 45-50 HRC. For industrial gearboxes.",
                "image_path": "images/6/IMG_3701.jpg"
            },
            {
                "material_number": "SP007",
                "description": "Belt - V-Belt",
                "category": "Power Transmission",
                "manufacturer": "Gates",
                "specifications": "A-section V-belt. Length: A-55. Top width: 1/2\". Height: 5/16\". For industrial drives. Temperature range: -40°F to +185°F."
            },
            {
                "material_number": "SP008",
                "description": "Sensor - Pressure Transmitter",
                "category": "Sensors",
                "manufacturer": "Honeywell",
                "specifications": "4-20mA pressure transmitter. Range: 0-100 PSI. Accuracy: ±0.25% FS. Output: 4-20mA. Power: 12-30V DC. For process control applications."
            },
            {
                "material_number": "SP009",
                "description": "Hose - Hydraulic Hose",
                "category": "Hydraulics",
                "manufacturer": "Parker",
                "specifications": "1/4\" hydraulic hose. Working pressure: 3,000 PSI. Burst pressure: 12,000 PSI. Temperature range: -40°F to +212°F. SAE 100R2AT specification."
            },
            {
                "material_number": "SP010",
                "description": "Switch - Limit Switch",
                "category": "Switches",
                "manufacturer": "Honeywell",
                "specifications": "Mechanical limit switch. SPDT contacts. Operating force: 2-4 oz. Electrical rating: 10A @ 120V AC. IP65 protection. For position sensing."
            }
        ]
        
        for part_data in sample_parts:
            spare_part = SparePart(**part_data)
            db.add(spare_part)
        
        db.commit()
        print(f"Successfully created {len(sample_parts)} sample spare parts.")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_tables()
    create_sample_data() 