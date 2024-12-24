# Speed Rush 2D - Backend API 🏎️

AI-powered car sprite generation API for Speed Rush 2D game. This service uses FastAPI, Stability AI, and OpenAI to generate custom car sprites with different styles and characteristics.

## 🚀 Features

- AI-powered car sprite generation
- Multiple design styles:
  - Pixel Art 🎮
  - Realistic 📸
  - Cartoon 🎨
  - Minimalist ⚪
- Automatic vehicle traits generation
- Automatic background removal
- RESTful API with FastAPI

## 🛠️ Technologies

- Python 3.11+
- FastAPI
- Stability AI API
- OpenAI API
- rembg (for background removal)
- Railway for deployment

## 📋 Requirements

- Python 3.11 or higher
- Stability AI API Key
- OpenAI API Key
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

# Edit .env and add your API keys
STABILITY_API_KEY=your_api_key_here
OPENAI_API_KEY=your_api_key_here
```

## 🚀 Usage

### Start the server locally:
```bash
uvicorn app.main:app --reload
```

### Available Endpoints:

#### Generate Car
```http
POST /api/cars/generate
```

Payload:
```json
{
    "prompt": "a red futuristic sports car",
    "style": "cartoon"
}
```

Available styles:
- `pixel_art`
- `realistic`
- `cartoon`
- `minimalist`

Response:
```json
{
    "image": {
        "data": "base64_string",
        "content_type": "image/png",
        "filename": "car_sprite.png"
    },
    "metadata": {
        "traits": {
            "speed": 1-10,
            "acceleration": 1-10,
            "handling": 1-10,
            "drift_factor": 1-10,
            "turn_factor": 1-10,
            "max_speed": 1-10
        }
    }
}
```

#### Health Check
```http
GET /health
```

## 📝 Usage Examples

### TypeScript/React
```typescript
const API_URL = "https://speed-rush-2d-backend-production.up.railway.app";

enum CarStyle {
    PIXEL_ART = "pixel_art",
    REALISTIC = "realistic",
    CARTOON = "cartoon",
    MINIMALIST = "minimalist"
}

const generateCar = async (prompt: string, style: CarStyle) => {
    const response = await fetch(`${API_URL}/api/cars/generate`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            prompt,
            style
        })
    });

    if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
    }

    return await response.json();
};
```

### Python
```python
import requests

API_URL = "https://speed-rush-2d-backend-production.up.railway.app"

def generate_car(prompt: str, style: str = "cartoon"):
    response = requests.post(
        f"{API_URL}/api/cars/generate",
        json={
            "prompt": prompt,
            "style": style
        }
    )
    response.raise_for_status()
    return response.json()
```

## 🌐 Deployment

The service is deployed on Railway. To deploy your own instance:

1. Create a Railway account
2. Connect your GitHub repository
3. Set up environment variables:
   - `STABILITY_API_KEY`
   - `OPENAI_API_KEY`
4. Done! Railway will handle automatic deployments

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome. Please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## ✨ Credits

- Stability AI for their image generation API
- OpenAI for their API
- rembg for the background removal tool
- Railway for hosting

## 📚 API Documentation

Full API documentation is available at:
- Swagger UI: `https://speed-rush-2d-backend-production.up.railway.app/docs`
- ReDoc: `https://speed-rush-2d-backend-production.up.railway.app/redoc`
