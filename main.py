from typing import Union
from fastapi import FastAPI
from transformers import pipeline
# All Pydantic models inherit from BaseModel, 
# and it serves as the foundation for defining the data structure, 
# applying validations, and enabling automatic parsing
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator

# IMPORTANT: Load the model ONCE when the app starts (not on every request)
# This is a critical performance optimization
print("Loading sentiment analysis model...")
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)
print("Model loaded successfully!")


# Create FastAPI app instance
app = FastAPI()

# Instrument the app and expose a /metric endpoint
Instrumentator().instrument(app).expose(app)


# Root endpoint to check if API is running
@app.get("/")
def read_root():
    return {"message": "Sentiment Analysis API is running!"}


# Define the request body structure
class TextInput(BaseModel):
    text: str


# Define a POST endpoint (e.g., /predict) that accepts a string of text.
@app.post("/predict")
def predict_sentiment(input_data: TextInput):
    # Get the text from the request
    text = input_data.text
    
    # Run inference
    result = sentiment_pipeline(text)
    
    # Return the result as JSON
    return {
        "input_text": text,
        "prediction": result[0]
    }