# ml-sentiment-analysis-api

# Sentiment Analysis API

A FastAPI-based REST API that performs sentiment analysis on text using a pre-trained DistilBERT model from Hugging Face.

## Description

This project provides a simple, containerized inference service for sentiment analysis. It uses the `distilbert-base-uncased-finetuned-sst-2-english` model to classify text as either positive or negative sentiment with a confidence score.

## Prerequisites

- **Docker**: Ensure Docker is installed on your system
  - [Install Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/)
  - [Install Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
  - [Install Docker Engine for Linux](https://docs.docker.com/engine/install/)

## How to Run

### 1. Build the Docker Image

```bash
docker build -t ml-inference-api .
```

This will create a Docker image named `ml-inference-api`. The first build may take 5-15 minutes as it downloads PyTorch and the transformer model.

### 2. Run the Docker Container

```bash
docker run -p 8000:8000 ml-inference-api
```

The API will be available at `http://localhost:8000`

To run in detached mode (background):
```bash
docker run -d -p 8000:8000 ml-inference-api
```

## API Usage

### Check API Status

```bash
curl http://localhost:8000
```

**Response:**
```json
{
  "message": "Sentiment Analysis API is running!"
}
```

### Predict Sentiment

Send a POST request to the `/predict` endpoint with JSON containing the text to analyze:

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "I love this product! It is amazing!"}'
```

**Response:**
```json
{
  "input_text": "I love this product! It is amazing!",
  "prediction": {
    "label": "POSITIVE",
    "score": 0.9998
  }
}
```

### Example with Negative Sentiment

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "This is terrible and disappointing."}'
```

**Response:**
```json
{
  "input_text": "This is terrible and disappointing.",
  "prediction": {
    "label": "NEGATIVE",
    "score": 0.9995
  }
}
```

## Interactive API Documentation

FastAPI automatically generates interactive API documentation. Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Development

### Local Development (without Docker)

If you want to run the project locally for development:

```bash
# Create a virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the development server
uvicorn main:app --reload
```

### Stopping the Server

- If running in foreground: Press `Ctrl + C`
- If you forgot to stop properly and the port is in use:

```bash
# Find the process using port 8000
lsof -i:8000

# Kill the process (replace PID with actual process ID)
kill -9 PID
```

### Deactivate Virtual Environment

```bash
deactivate
```

## Project Structure

```
.
├── Dockerfile
├── requirements.txt
├── main.py
└── README.md
```

## Technologies Used

- **FastAPI**: Modern web framework for building APIs
- **Transformers**: Hugging Face library for NLP models
- **PyTorch**: Deep learning framework
- **Uvicorn**: ASGI server for serving the API
- **Docker**: Containerization platform

## Model Information

- **Model**: `distilbert-base-uncased-finetuned-sst-2-english`
- **Task**: Binary sentiment classification (Positive/Negative)
- **Model Size**: ~250MB
- **Framework**: PyTorch + Transformers

## License

This project is for educational purposes.