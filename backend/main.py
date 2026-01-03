from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from datetime import datetime

from models import SparePart, SparePartCreate, SparePartResponse, SearchResult, ImageUploadResponse
from database import get_db, create_tables

# Create FastAPI app
app = FastAPI(
    title="Spare Parts Identification System",
    description="AI-powered spare parts identification using image recognition",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://192.168.1.85:3000",
        "https://localhost:3000",
        "https://127.0.0.1:3000",
        "https://192.168.1.85:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Mount static files
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
app.mount("/images", StaticFiles(directory="images"), name="images")

# Initialize AI service
ai_service = None
ai_available = False

try:
    from ai_service import AIService
    ai_service = AIService()
    ai_available = True
    print("✅ AI service initialized successfully")
except Exception as e:
    print(f"⚠️  AI service initialization failed: {e}")
    print("   The application will run without AI features")
    ai_service = None
    ai_available = False

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

@app.get("/")
async def root():
    return {"message": "Spare Parts Identification System API"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    global ai_available
    if ai_service:
        try:
            ai_available = ai_service.is_model_available()
        except:
            ai_available = False
    
    ai_provider = "Not configured"
    if ai_available and ai_service:
        try:
            from ai_service import CLIP_AVAILABLE
            ai_provider = "CLIP Semantic Matching" if CLIP_AVAILABLE else "SIFT-based Image Similarity"
        except:
            ai_provider = "Image Matching Available"

    return {
        "status": "healthy",
        "ai_model_available": ai_available,
        "ai_provider": ai_provider,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/upload-image", response_model=ImageUploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload an image and find matching spare parts using AI
    """
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Save uploaded file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Read image data for AI analysis
        with open(file_path, "rb") as f:
            image_data = f.read()
        
        # Get all spare parts from database
        spare_parts = db.query(SparePart).all()
        spare_parts_data = [
            {
                "material_number": part.material_number,
                "description": part.description,
                "category": part.category,
                "manufacturer": part.manufacturer,
                "specifications": part.specifications,
                "image_path": part.image_path
            }
            for part in spare_parts
        ]
        
        # Analyze image with AI
        if ai_service and ai_available:
            ai_matches = ai_service.analyze_image(image_data, spare_parts_data)
        else:
            # Fallback: return first few parts with low confidence
            ai_matches = []
            for i, part in enumerate(spare_parts_data[:3]):
                ai_matches.append({
                    "material_number": part['material_number'],
                    "confidence_score": 0.3 - (i * 0.1),
                    "match_reason": "AI service not available - please verify manually"
                })
        
        # Convert AI matches to SearchResult objects
        search_results = []
        for match in ai_matches:
            material_number = match.get("material_number")
            if material_number:
                # Find the spare part in database
                spare_part = db.query(SparePart).filter(
                    SparePart.material_number == material_number
                ).first()
                
                if spare_part:
                    search_result = SearchResult(
                        spare_part=SparePartResponse.model_validate(spare_part),
                        confidence_score=match.get("confidence_score", 0.0),
                        match_reason=match.get("match_reason", "AI analysis")
                    )
                    search_results.append(search_result)
        
        # Sort by confidence score (highest first)
        search_results.sort(key=lambda x: x.confidence_score, reverse=True)
        
        return ImageUploadResponse(
            message=f"Image uploaded successfully. Found {len(search_results)} potential matches.",
            search_results=search_results
        )
        
    except Exception as e:
        # Clean up uploaded file on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.get("/spare-parts", response_model=List[SparePartResponse])
async def get_spare_parts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all spare parts with pagination"""
    spare_parts = db.query(SparePart).offset(skip).limit(limit).all()
    return [SparePartResponse.model_validate(part) for part in spare_parts]

@app.get("/spare-parts/{material_number}", response_model=SparePartResponse)
async def get_spare_part(material_number: str, db: Session = Depends(get_db)):
    """Get a specific spare part by material number"""
    spare_part = db.query(SparePart).filter(
        SparePart.material_number == material_number
    ).first()
    
    if not spare_part:
        raise HTTPException(status_code=404, detail="Spare part not found")
    
    return SparePartResponse.model_validate(spare_part)

@app.post("/spare-parts", response_model=SparePartResponse)
async def create_spare_part(
    spare_part: SparePartCreate,
    db: Session = Depends(get_db)
):
    """Create a new spare part"""
    # Check if material number already exists
    existing = db.query(SparePart).filter(
        SparePart.material_number == spare_part.material_number
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Material number already exists")
    
    db_spare_part = SparePart(**spare_part.dict())
    db.add(db_spare_part)
    db.commit()
    db.refresh(db_spare_part)
    
    return SparePartResponse.model_validate(db_spare_part)

@app.get("/search")
async def search_spare_parts(
    query: str,
    db: Session = Depends(get_db)
):
    """Search spare parts by description or material number"""
    spare_parts = db.query(SparePart).filter(
        (SparePart.description.contains(query)) |
        (SparePart.material_number.contains(query))
    ).all()
    
    return [SparePartResponse.model_validate(part) for part in spare_parts]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 