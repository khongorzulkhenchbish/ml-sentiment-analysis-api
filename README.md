# Sentiment Analysis API

A FastAPI-based REST API that performs sentiment analysis on text using a pre-trained DistilBERT model from Hugging Face. This project demonstrates a complete MLOps workflow including containerization, Kubernetes deployment, and CI/CD automation.

## Description

This project provides a simple, containerized inference service for sentiment analysis. It uses the `distilbert-base-uncased-finetuned-sst-2-english` model to classify text as either positive or negative sentiment with a confidence score.

## Table of Contents

- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [CI/CD Pipeline](#cicd-pipeline)
- [API Usage](#api-usage)
- [Technologies Used](#technologies-used)

---

## Local Development

### Prerequisites

- Python 3.9+
- pip

### Setup

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

---

## Docker Deployment

### Prerequisites

- **Docker**: Ensure Docker is installed on your system
  - [Install Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/)
  - [Install Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
  - [Install Docker Engine for Linux](https://docs.docker.com/engine/install/)

### Build the Docker Image

```bash
docker build -t ml-inference-api .
```

This will create a Docker image named `ml-inference-api`. The first build may take 5-15 minutes as it downloads PyTorch and the transformer model.

### Run the Docker Container

```bash
docker run -p 8000:8000 ml-inference-api
```

The API will be available at `http://localhost:8000`

To run in detached mode (background):
```bash
docker run -d -p 8000:8000 ml-inference-api
```

### Docker Hub

The Docker image is publicly available on Docker Hub:

```bash
# Pull the image
docker pull khenchbishkhongorzul/ml-sentiment-analysis-api:latest

# Run locally (without Kubernetes)
docker run -p 8000:8000 khenchbishkhongorzul/ml-sentiment-analysis-api:latest
```

**Docker Hub Repository**: https://hub.docker.com/r/khenchbishkhongorzul/ml-sentiment-analysis-api

---

## Kubernetes Deployment

### Prerequisites

- **Minikube**: Local Kubernetes cluster
  - [Install Minikube](https://minikube.sigs.k8s.io/docs/start/)
- **kubectl**: Kubernetes command-line tool
  - Usually installed with Minikube or [install separately](https://kubernetes.io/docs/tasks/tools/)

### Setup Local Kubernetes Cluster

```bash
# Start Minikube
minikube start

# Verify cluster is running
kubectl cluster-info
```

### Deploy to Kubernetes

The application uses two Kubernetes manifests located in the `k8s/` directory:
- `deployment.yaml` - Defines the deployment and replica configuration
- `service.yaml` - Exposes the application via NodePort

```bash
# Apply the deployment
kubectl apply -f k8s/deployment.yaml

# Apply the service
kubectl apply -f k8s/service.yaml

# Verify deployment
kubectl get deployments
kubectl get pods
kubectl get services
```

### Access the Application

```bash
# List all services
minikube service list

# Get the service URL
minikube service sentiment-api-service --url
```

This will output a URL like `http://127.0.0.1:55610`. Use this URL to access your API.

### Test the Kubernetes Deployment

```bash
# Get the service URL
SERVICE_URL=$(minikube service sentiment-api-service --url)

# Test the API
curl -X POST "$SERVICE_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "This is amazing!"}'
```

You can also use **Postman** or any HTTP client with the URL from `minikube service`.

### Scaling

Scale the deployment to handle more traffic:

```bash
# Scale up to 3 replicas
kubectl scale deployment sentiment-api --replicas=3

# Verify pods are running
kubectl get pods

# Scale back down to 1 replica
kubectl scale deployment sentiment-api --replicas=1
```

### Useful Kubernetes Commands

```bash
# View pod logs
kubectl logs <pod-name>

# Describe a pod (useful for troubleshooting)
kubectl describe pod <pod-name>

# Delete deployment and service
kubectl delete -f k8s/deployment.yaml
kubectl delete -f k8s/service.yaml

# Stop Minikube
minikube stop

# Delete Minikube cluster
minikube delete
```

---

## CI/CD Pipeline

This project uses **GitHub Actions** to automate testing, building, and deployment using a **GitOps** approach.

### Pipeline Overview

The CI/CD pipeline consists of three jobs:

1. **Test** - Runs unit tests on the code
2. **Build and Push** - Builds Docker image and pushes to Docker Hub
3. **Deploy** - Updates Kubernetes manifests with new image tag

### Workflow File

The pipeline is defined in `.github/workflows/ci-pipeline.yml`

### How It Works (GitOps Pattern)

1. **Code Change**: You push code changes to the `main` branch
2. **Automated Testing**: GitHub Actions runs tests
3. **Build Docker Image**: If tests pass, a new Docker image is built and tagged with:
   - `latest` tag
   - Commit SHA tag (e.g., `abc123def456...`)
4. **Push to Docker Hub**: Both image tags are pushed to Docker Hub
5. **Update Manifest**: The pipeline updates `k8s/deployment.yaml` with the new commit SHA tag
6. **Commit Back**: The updated manifest is committed back to the repository
7. **Local Pull**: You run `git pull` locally to get the updated manifest
8. **Apply Changes**: Run `kubectl apply -f k8s/deployment.yaml` to deploy the new version

### Setup GitHub Actions

#### 1. Add Docker Hub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions → New repository secret

Add two secrets:
- `DOCKERHUB_USERNAME` - Your Docker Hub username
- `DOCKERHUB_TOKEN` - Your Docker Hub access token (create at https://hub.docker.com/settings/security)

#### 2. Enable Workflow Permissions

The workflow needs write permissions to commit updated manifests back to the repository. This is already configured in the workflow file:

```yaml
permissions:
  contents: write
```

### Testing the Full Pipeline

1. **Make a code change** to `main.py`:
   ```python
   # Example: Change the welcome message
   return {"message": "Sentiment Analysis API v2 is running!"}
   ```

2. **Commit and push**:
   ```bash
   git add .
   git commit -m "Update welcome message"
   git push
   ```

3. **Watch the pipeline**:
   - Go to the **Actions** tab on GitHub
   - You'll see the workflow running with three jobs: `test`, `build-and-push`, and `deploy`

4. **Verify the commit**:
   - After the pipeline finishes, check your **Commits** page
   - You'll see a new commit from `github-actions[bot]` with message `[CI SKIP] Update image tag to <commit-sha>`
   - Click the commit to see the changed `image:` line in `k8s/deployment.yaml`

5. **Pull the changes locally**:
   ```bash
   git pull
   ```

6. **Apply to Kubernetes**:
   ```bash
   kubectl apply -f k8s/deployment.yaml
   ```

7. **Verify the update**:
   - Kubernetes will perform a rolling update to the new image
   - Test the API to see your changes:
   ```bash
   SERVICE_URL=$(minikube service sentiment-api-service --url)
   curl $SERVICE_URL
   ```

### Pipeline Features

✅ **Automated Testing** - Runs tests before building  
✅ **Multi-tag Images** - Tags with both `latest` and commit SHA  
✅ **GitOps Pattern** - Infrastructure as code with version control  
✅ **CI Skip** - Prevents infinite loops with `[CI SKIP]` commit message  
✅ **Secure** - Uses GitHub secrets for credentials  

### Workflow Triggers

The pipeline runs automatically on:
- Push to `main` branch
- Pull requests to `main` branch

**Note**: Commits with `[CI SKIP]` or `[skip ci]` in the message won't trigger the workflow.

---

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

### Interactive API Documentation

FastAPI automatically generates interactive API documentation. Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Technologies Used

- **FastAPI**: Modern web framework for building APIs
- **Transformers**: Hugging Face library for NLP models
- **PyTorch**: Deep learning framework
- **Uvicorn**: ASGI server for serving the API
- **Docker**: Containerization platform
- **Kubernetes**: Container orchestration platform
- **Minikube**: Local Kubernetes environment
- **GitHub Actions**: CI/CD automation

## Model Information

- **Model**: `distilbert-base-uncased-finetuned-sst-2-english`
- **Task**: Binary sentiment classification (Positive/Negative)
- **Model Size**: ~250MB
- **Framework**: PyTorch + Transformers

## Project Structure

```
.
├── .github/
│   └── workflows/
│       └── ci-pipeline.yml
├── k8s/
│   ├── deployment.yaml
│   └── service.yaml
├── Dockerfile
├── requirements.txt
├── main.py
└── README.md
```

## License

This project is for educational purposes.