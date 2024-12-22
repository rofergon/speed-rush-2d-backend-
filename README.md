# Speed Rush 2D - Car Sprite Generator

This project is a Python backend that generates top-down 2D car sprites using OpenAI's API.

## Features

- Car sprite generation using DALL-E 3
- Image validation using GPT-4 Vision
- Automatic background removal
- REST API built with FastAPI

## Requirements

- Python 3.8+
- OpenAI API Key

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Running the Server

```bash
uvicorn app.main:app --reload
```

The server will be available at `http://localhost:8000`

## API Endpoints

### POST /api/cars/generate

Generates a new car sprite.

Request body:
```json
{
    "prompt": "red sports car"
}
```

Response:
```json
{
    "success": true,
    "message": "Sprite generated successfully",
    "image_data": "base64_image_data"
}
```

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## AWS Deployment

To deploy on AWS:

1. Create an EC2 instance or ECS service
2. Configure environment variables
3. Install dependencies
4. Run with gunicorn:
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```
