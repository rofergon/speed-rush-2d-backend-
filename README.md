# Speed Rush 2D - Backend API 🏎️

AI-powered car sprite generation API for Speed Rush 2D game. This service uses FastAPI and Stability AI to generate custom car sprites and their components with different styles and characteristics.

## 🚀 Features

- AI-powered sprite generation for:
  - Complete car designs 🚗
  - Engine components 🔧
  - Transmission systems ⚙️
  - Wheel sets 🛞
- Multiple design styles:
  - Pixel Art 🎮
  - Realistic 📸
  - Cartoon 🎨
  - Minimalist ⚪
- Automatic vehicle traits generation
- Automatic background removal
- RESTful API with FastAPI
- Parallel image generation
- Consistent color schemes across components

## 🛠️ Technologies

- Python 3.11+
- FastAPI
- Stability AI API
- rembg (for background removal)
- Railway for deployment

## 📋 Requirements

- Python 3.11 or higher
- Stability AI API Key
- Internet Connection

## 🔧 Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/speed-rush-2d-backend.git
cd speed-rush-2d-backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Create .env file
cp .env.example .env

# Edit .env and add your API key
STABILITY_API_KEY=your_api_key_here
```

## 🚀 Usage

### Start the server locally:
```bash
uvicorn app.main:app --reload --port 8080
```

### Available Endpoints:

#### Generate Car and Components
```http
POST /api/cars/generate
```

Payload:
```json
{
    "prompt": "string",
    "style": "cartoon",
    "engineType": "standard",
    "transmissionType": "manual",
    "wheelsType": "sport"
}
```

Available parameters:
- `style`: pixel_art, realistic, cartoon, minimalist
- `engineType`: standard, performance, eco
- `transmissionType`: manual, automatic, sequential
- `wheelsType`: sport, racing, offroad

Response:
```json
{
    "carImageURI": "https://gateway.lighthouse.storage/ipfs/...",
    "parts": [
        {
            "partType": "ENGINE",
            "stat1": 7,
            "stat2": 6,
            "stat3": 8,
            "imageURI": "https://gateway.lighthouse.storage/ipfs/..."
        },
        {
            "partType": "TRANSMISSION",
            "stat1": 8,
            "stat2": 7,
            "stat3": 9,
            "imageURI": "https://gateway.lighthouse.storage/ipfs/..."
        },
        {
            "partType": "WHEELS",
            "stat1": 6,
            "stat2": 8,
            "stat3": 7,
            "imageURI": "https://gateway.lighthouse.storage/ipfs/..."
        }
    ]
}
```

#### Health Check
```http
GET /health
```

## 📝 Usage Examples

### Python
```python
import requests

API_URL = "http://localhost:8080"

def generate_car(style: str = "cartoon", 
                engine_type: str = "standard",
                transmission_type: str = "manual",
                wheels_type: str = "sport"):
    response = requests.post(
        f"{API_URL}/api/cars/generate",
        json={
            "prompt": "string",
            "style": style,
            "engineType": engine_type,
            "transmissionType": transmission_type,
            "wheelsType": wheels_type
        }
    )
    response.raise_for_status()
    return response.json()
```

### TypeScript/React
```typescript
const API_URL = "http://localhost:8080";

enum CarStyle {
    PIXEL_ART = "pixel_art",
    REALISTIC = "realistic",
    CARTOON = "cartoon",
    MINIMALIST = "minimalist"
}

interface GenerateCarRequest {
    prompt: string;
    style: CarStyle;
    engineType: "standard" | "performance" | "eco";
    transmissionType: "manual" | "automatic" | "sequential";
    wheelsType: "sport" | "racing" | "offroad";
}

const generateCar = async (params: GenerateCarRequest) => {
    const response = await fetch(`${API_URL}/api/cars/generate`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(params)
    });

    if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
    }

    return await response.json();
};
```

## 🎨 Image Generation Details

The system generates images using Stability AI's API with the following characteristics:

- Each component (car, engine, transmission, wheels) uses specific reference images
- Control strength of 0.65 for balanced creativity and structure
- 40 generation steps for high quality
- Automatic background removal
- Consistent color schemes across all components
- Style-specific prompts for each component type

## 🌐 Deployment

The service can be deployed on Railway:

1. Create a Railway account
2. Connect your GitHub repository
3. Set up environment variable:
   - `STABILITY_API_KEY`
4. Done! Railway will handle automatic deployments

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ✨ Credits

- Stability AI for their image generation API
- rembg for the background removal tool
- Railway for hosting

## 📚 API Documentation

Full API documentation is available at:
- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`
