# Setup Guide - Spare Parts Identification System

This guide will help you set up and run the AI-powered spare parts identification system using OpenAI's GPT-4 Vision API.

## Prerequisites

Before starting, ensure you have the following installed:

- **Python 3.8+** - [Download here](https://www.python.org/downloads/)
- **Node.js 14+** - [Download here](https://nodejs.org/)
- **npm** - Usually comes with Node.js
- **OpenAI API Key** - [Get one here](https://platform.openai.com/api-keys)

## Quick Start (Recommended)

1. **Clone or download the project**
   ```bash
   cd spareparts
   ```

2. **Set up your OpenAI API key**
   ```bash
   export OPENAI_API_KEY="your_openai_api_key_here"
   ```

3. **Run the startup script**
   ```bash
   ./start.sh
   ```

   This script will:
   - Install all dependencies
   - Set up the database with sample data
   - Start both backend and frontend servers

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Manual Setup

If you prefer to set up manually or the startup script doesn't work:

### Backend Setup

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
   ```

4. **Set up database**
   ```bash
   python sample_data.py
   ```

5. **Start backend server**
   ```bash
   python main.py
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start frontend server**
   ```bash
   npm start
   ```

## OpenAI API Setup (Required for AI Features)

The application uses OpenAI's GPT-4 Vision API for AI-powered image recognition. Follow these steps:

1. **Get an OpenAI API Key**
   - Visit [OpenAI Platform](https://platform.openai.com/api-keys)
   - Sign up or log in to your account
   - Create a new API key

2. **Set the API Key**
   
   **Option A: Environment Variable (Recommended)**
   ```bash
   export OPENAI_API_KEY="your_api_key_here"
   ```
   
   **Option B: Create a .env file**
   ```bash
   # In the backend directory
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   ```

3. **Verify API Key**
   - The application will automatically check if the API key is valid
   - You can test it by visiting http://localhost:8000/health

## Usage

### Basic Workflow

1. **Open the application** in your browser at http://localhost:3000

2. **Take a photo** of a spare part:
   - Click "Start Camera" to use your device's camera
   - Or upload an image file

3. **View results** - The AI will analyze the image and show potential matches

4. **Select a match** to view detailed information

### Adding Your Own Parts

You can add your own spare parts to the database:

1. **Via API** (for developers):
   ```bash
   curl -X POST "http://localhost:8000/spare-parts" \
     -H "Content-Type: application/json" \
     -d '{
       "material_number": "YOUR_PART_NUMBER",
       "description": "Part description",
       "category": "Category",
       "manufacturer": "Manufacturer",
       "specifications": "Technical specifications"
     }'
   ```

2. **Via the web interface** - Use the search and management features

## Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Database
DATABASE_URL=sqlite:///./spareparts.db

# API Settings
API_HOST=0.0.0.0
API_PORT=8000

# Upload Settings
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760
```

### Customizing AI Recognition

Edit `backend/ai_service.py` to:
- Change the AI model (e.g., to gpt-4o)
- Modify recognition prompts
- Adjust confidence thresholds

## Troubleshooting

### Common Issues

1. **"AI model not available"**
   - Check if OPENAI_API_KEY is set correctly
   - Verify your API key is valid at https://platform.openai.com/api-keys
   - Ensure you have sufficient credits in your OpenAI account

2. **"Camera not working"**
   - Ensure you're using HTTPS or localhost
   - Check browser permissions for camera access
   - Try uploading an image file instead

3. **"Backend connection failed"**
   - Check if backend is running on port 8000
   - Verify no firewall blocking the port
   - Check backend logs for errors

4. **"Database errors"**
   - Delete `spareparts.db` and restart
   - Run `python sample_data.py` to recreate database

5. **"OpenAI API errors"**
   - Check your API key is correct
   - Verify you have sufficient credits
   - Check OpenAI service status at https://status.openai.com/

### Logs and Debugging

- **Backend logs**: Check terminal where backend is running
- **Frontend logs**: Open browser developer tools (F12)
- **OpenAI API logs**: Check your OpenAI dashboard

## Cost Considerations

Using OpenAI's GPT-4 Vision API incurs costs:

- **GPT-4 Vision**: ~$0.01-0.03 per image analysis
- **Cost depends on**: Image size, token usage, and API tier
- **Monitoring**: Check your usage at https://platform.openai.com/usage

For production use, consider:
- Setting up usage limits
- Implementing caching for repeated images
- Using a lower-cost model for initial screening

## Production Deployment

For production use, consider:

1. **Use a production database** (PostgreSQL, MySQL)
2. **Set up proper authentication**
3. **Use HTTPS**
4. **Configure proper logging**
5. **Set up monitoring and alerts**
6. **Implement rate limiting for API calls**
7. **Set up cost monitoring for OpenAI usage**

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the API documentation at http://localhost:8000/docs
3. Check the logs for error messages
4. Ensure all prerequisites are properly installed
5. Verify your OpenAI API key and credits

## License

This project is licensed under the MIT License. 