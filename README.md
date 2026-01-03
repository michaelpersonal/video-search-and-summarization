# Spare Parts Identification System

A web application that uses AI-powered semantic image matching to identify spare parts from photos. This system allows warehouse workers and field technicians to quickly look up material numbers by taking photos of parts.

## Features

- 📸 **Photo Capture**: Take photos using device camera or upload images
- 🤖 **AI Recognition**: CLIP-based semantic image matching for accurate part identification
- 🔍 **Smart Search**: Find matching parts from database using visual similarity
- 📱 **Mobile-Friendly**: Responsive design for phones and tablets
- ⚡ **Fast Results**: Quick identification and display of matches

## Tech Stack

- **Frontend**: React.js with TypeScript
- **Backend**: FastAPI (Python)
- **AI Model**: OpenAI CLIP (Contrastive Language-Image Pre-training)
- **ML Framework**: PyTorch with Transformers (Hugging Face)
- **Database**: SQLite for parts storage
- **Styling**: CSS with modern design

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- A webcam (for camera capture feature)

### Option 1: Automated Setup (Recommended)

1. **Start Backend Server**
   ```bash
   # In one terminal:
   ./start_backend.sh
   ```

2. **Start Frontend Server**
   ```bash
   # In another terminal:
   ./start_frontend.sh
   ```

3. **Access the App**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Option 2: Manual Setup

#### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt

   # Install additional ML dependencies
   pip install torch transformers safetensors
   ```

4. **Configure environment (optional)**
   ```bash
   # Create .env file for custom configuration
   echo "OPENAI_API_KEY=your_key_here" > .env
   ```

5. **Set up database**
   ```bash
   python sample_data.py
   ```

6. **Start backend server**
   ```bash
   python main.py
   ```

#### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure API endpoint**
   ```bash
   # Edit frontend/.env to set API URL (default: http://localhost:8000)
   echo "REACT_APP_API_URL=http://localhost:8000" > .env
   ```

4. **Start frontend server**
   ```bash
   npm start
   ```

## Usage

### Identifying a Part

1. **Open the app** at http://localhost:3000
2. **Choose input method**:
   - Click **"Start Camera"** to take a live photo
   - Click **"Upload Image"** to select an existing photo
3. **Capture/Upload** the spare part image
4. **View results**: The AI will identify matching parts with confidence scores
5. **Select a match** to view detailed information

### Camera Permissions

When using the camera feature for the first time:

1. **Browser will ask for permission** - Click "Allow"
2. **On macOS**: System Settings → Privacy & Security → Camera → Enable your browser
3. **On Windows**: Settings → Privacy → Camera → Allow apps to access camera

## AI Model Details

### CLIP Semantic Matching

The system uses OpenAI's CLIP (Contrastive Language-Image Pre-training) model for semantic image matching:

- **Model**: `openai/clip-vit-base-patch32`
- **Method**: Cosine similarity between image embeddings
- **Threshold**: 90% similarity for matches
- **Pre-computed**: Features are computed once and stored for fast matching

### How It Works

1. **Feature Extraction**: When you upload an image, CLIP extracts visual features
2. **Similarity Comparison**: Compares features with pre-computed database embeddings
3. **Ranking**: Returns matches above 90% similarity threshold
4. **Display**: Shows best matches with confidence scores

## Project Structure

```
spareparts/
├── backend/                    # FastAPI backend
│   ├── main.py                # Main application and API routes
│   ├── models.py              # SQLAlchemy database models
│   ├── database.py            # Database configuration
│   ├── ai_service.py          # CLIP-based image matching
│   ├── config.py              # Configuration settings
│   ├── requirements.txt       # Python dependencies
│   ├── images/                # Stored part images
│   ├── part_image_embeddings.npy       # Pre-computed CLIP features
│   └── part_image_embeddings_map.json  # Feature-to-part mapping
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── CameraCapture.tsx    # Camera interface
│   │   │   └── SearchResults.tsx    # Results display
│   │   ├── services/
│   │   │   └── api.ts              # Backend API client
│   │   ├── App.tsx                 # Main application
│   │   └── types.ts                # TypeScript types
│   ├── public/
│   ├── package.json
│   └── .env                   # Frontend configuration
├── start_backend.sh           # Backend startup script
├── start_frontend.sh          # Frontend startup script
├── start.sh                   # Combined startup script
├── README.md                  # This file
└── AGENT.md                   # AI agent development documentation
```

## Configuration

### Backend Configuration

**Environment Variables** (`backend/.env`):
```bash
# Optional: OpenAI API key (not currently used, but reserved for future features)
OPENAI_API_KEY=your_key_here
```

**AI Model Settings** (`backend/ai_service.py`):
- Similarity threshold: 0.9 (90%)
- CLIP model: openai/clip-vit-base-patch32
- Feature dimensions: 512

### Frontend Configuration

**Environment Variables** (`frontend/.env`):
```bash
# Backend API URL
REACT_APP_API_URL=http://localhost:8000
```

## Adding New Parts to Database

To add new spare parts with image matching:

1. **Add part to database**:
   ```python
   # In backend directory
   python add_missing_parts.py
   ```

2. **Compute CLIP features**:
   ```python
   python compute_image_embeddings.py
   ```

3. **Restart backend** to load new features

## API Endpoints

The backend provides the following REST API endpoints:

- `GET /health` - System health and AI status
- `POST /upload-image` - Upload image and get matching parts
- `GET /spare-parts` - List all spare parts
- `GET /spare-parts/{material_number}` - Get specific part details
- `GET /docs` - Interactive API documentation (Swagger UI)

## Troubleshooting

### Common Issues

#### 1. Frontend Shows "API Unhealthy" or "AI Unavailable"

**Solution**:
- Clear browser cache (Cmd+Shift+R or Ctrl+Shift+R)
- Check backend is running: `curl http://localhost:8000/health`
- Verify `.env` files have correct URLs
- Check console for CORS errors

#### 2. Camera Access Denied

**Solution**:
- **Browser permissions**: Click camera icon in address bar → "Always allow"
- **macOS**: System Settings → Privacy & Security → Camera → Enable browser
- **Windows**: Settings → Privacy → Camera → Allow apps
- **Camera in use**: Close other apps using camera (Zoom, Teams, etc.)

#### 3. CLIP Model Loading Fails

**Error**: `torch.load requires PyTorch 2.6+`

**Solution**:
```bash
cd backend
source venv/bin/activate
pip install torch transformers safetensors
```

The app uses `use_safetensors=True` to bypass PyTorch version restrictions.

#### 4. No Matches Found

**Possible causes**:
- Part not in database (add it using `add_missing_parts.py`)
- Image quality too low (try better lighting/focus)
- Features not computed (run `compute_image_embeddings.py`)

#### 5. Port Already in Use

**Solution**:
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

#### 6. npm Install Fails

**Solution**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Debug Mode

Enable detailed logging:

1. **Backend**: Check logs in terminal where backend is running
2. **Frontend**: Open browser DevTools (F12) → Console tab
3. **API Testing**: Visit http://localhost:8000/docs for interactive testing

## Performance Optimization

- **Pre-computed features**: CLIP features are computed once and stored
- **Fast matching**: Cosine similarity is computed in milliseconds
- **Efficient storage**: Features stored in NumPy format for fast loading
- **Image optimization**: Camera captures at optimal resolution

## Browser Compatibility

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

**Note**: Camera features require HTTPS or localhost. Mobile browsers fully supported.

## Security Considerations

- API runs on localhost by default (not exposed to internet)
- No authentication required for local development
- Camera access requires user permission
- CORS configured for localhost origins only

## Future Enhancements

- [ ] Multi-language support
- [ ] Batch image processing
- [ ] Mobile app (React Native)
- [ ] Cloud deployment
- [ ] User authentication
- [ ] Part inventory management
- [ ] Integration with ERP systems
- [ ] Advanced analytics and reporting

## Contributing

This is a private project. For issues or improvements, contact the development team.

## License

MIT License

---

## Quick Reference

**Start App**:
```bash
./start_backend.sh    # Terminal 1
./start_frontend.sh   # Terminal 2
```

**Access**:
- App: http://localhost:3000
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

**Check Status**:
```bash
curl http://localhost:8000/health
```

**Stop All**:
```bash
# Ctrl+C in both terminals
# Or kill processes:
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```
