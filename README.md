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

## Monitoring and Observability

This project implements a full monitoring stack using **Prometheus** for metrics collection and **Grafana** for visualization, demonstrating production-ready observability practices.

### Overview

The monitoring setup includes:
- **Metrics Instrumentation**: FastAPI app exposes Prometheus metrics at `/metrics`
- **Prometheus**: Scrapes and stores metrics from the API
- **Grafana**: Visualizes metrics through custom dashboards
- **ServiceMonitor**: Kubernetes resource that configures Prometheus scraping

### Architecture

```
FastAPI App (/metrics) → ServiceMonitor → Prometheus → Grafana Dashboard
```

### Prerequisites

- **Helm**: Kubernetes package manager
  - macOS: `brew install helm`
  - Linux: `curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash`
- Running Kubernetes cluster (Minikube)
- Application deployed with metrics endpoint

### Setup Monitoring Stack

#### 1. Install Prometheus and Grafana

Add the Prometheus Helm repository:
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

Install the kube-prometheus-stack (includes Prometheus, Grafana, and Alertmanager):
```bash
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace
```

Verify installation:
```bash
# Watch pods being created
kubectl get pods -n monitoring --watch

# Check all resources
kubectl get all -n monitoring
```

Wait until all pods show `Running` status.

#### 2. Configure Prometheus to Scrape Your API

Update your service to include a port name (required for ServiceMonitor):

**k8s/service.yaml:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: sentiment-api-service
  labels:
    app: sentiment-api
spec:
  type: NodePort
  selector:
    app: sentiment-api
  ports:
  - name: http  # ← Port name is required
    protocol: TCP
    port: 80
    targetPort: 8000
```

Apply the updated service:
```bash
kubectl apply -f k8s/service.yaml
```

Create a ServiceMonitor to tell Prometheus where to scrape:

**k8s/servicemonitor.yaml:**
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: sentiment-api-monitor
  namespace: default
  labels:
    release: prometheus  # Critical: must match Prometheus release name
spec:
  selector:
    matchLabels:
      app: sentiment-api  # Must match service label
  endpoints:
  - port: http  # Must match service port name
    path: /metrics
    interval: 15s
```

Apply the ServiceMonitor:
```bash
kubectl apply -f k8s/servicemonitor.yaml
```

#### 3. Verify Metrics Collection

Port-forward to Prometheus:
```bash
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090
```

Open http://localhost:9090 and:
1. Go to **Status** → **Targets**
2. Look for `serviceMonitor/default/sentiment-api-monitor/0`
3. Verify endpoints show status "UP"

Test a query in the **Graph** tab:
```promql
up{job="sentiment-api-monitor"}
```

Should return `1` if scraping is successful.

### Access Grafana

Port-forward to Grafana:
```bash
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
```

Open http://localhost:3000

**Default credentials:**
- Username: `admin`
- Password: `prom-operator`

### Available Metrics

The application exposes the following Prometheus metrics:

| Metric | Description | Type |
|--------|-------------|------|
| `http_requests_total` | Total HTTP requests | Counter |
| `http_request_duration_seconds` | Request latency distribution | Histogram |
| `http_requests_inprogress` | Current requests being processed | Gauge |

### Creating Dashboards

#### Import Pre-built Dashboard

If you have the exported dashboard JSON:

1. In Grafana, go to **Dashboards** → **Import**
2. Click **Upload JSON file**
3. Select `grafana/sentiment-api-dashboard.json`
4. Click **Import**

#### Build Custom Dashboard

Create a new dashboard with these key panels:

**1. Request Rate (Requests per Second)**
```promql
sum(rate(http_requests_total[5m]))
```

**2. 95th Percentile Latency (milliseconds)**
```promql
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le)) * 1000
```

**3. Error Rate (5xx responses per second)**
```promql
sum(rate(http_requests_total{status=~"5.."}[5m]))
```

**4. Success Rate (%)**
```promql
(sum(rate(http_requests_total{status=~"2.."}[5m])) / sum(rate(http_requests_total[5m]))) * 100
```

**5. Request Count by Endpoint**
```promql
sum by (handler) (rate(http_requests_total[5m]))
```

**6. Average Response Time (milliseconds)**
```promql
(sum(rate(http_request_duration_seconds_sum[5m])) / sum(rate(http_request_duration_seconds_count[5m]))) * 1000
```

### Generate Test Traffic

To populate your dashboards with data:

```bash
# Get service URL
SERVICE_URL=$(minikube service sentiment-api-service --url)

# Send 100 test requests
for i in {1..100}; do
  curl -X POST "$SERVICE_URL/predict" \
    -H "Content-Type: application/json" \
    -d '{"text": "Test request '$i'"}' &
done

# Wait for all requests to complete
wait
```

Refresh your Grafana dashboard to see the metrics!

### Accessing Metrics Directly

You can also access the raw metrics endpoint:

```bash
# Port-forward to your app
kubectl port-forward <pod-name> 8000:8000

# View metrics
curl http://localhost:8000/metrics
```

Or through the Minikube service:
```bash
SERVICE_URL=$(minikube service sentiment-api-service --url)
curl $SERVICE_URL/metrics
```

### Monitoring Best Practices

✅ **Set up alerts**: Configure Alertmanager for critical metrics (high error rate, high latency)  
✅ **Monitor continuously**: Check dashboards regularly during development  
✅ **Establish baselines**: Know your normal request rates and latencies  
✅ **Track trends**: Use longer time ranges (24h, 7d) to spot patterns  
✅ **Document incidents**: Use annotations in Grafana to mark deployments and issues  

### Troubleshooting

**Prometheus not scraping:**
- Verify ServiceMonitor has `release: prometheus` label
- Check service has named port (`name: http`)
- Confirm ServiceMonitor is in same namespace as app
- Check Prometheus targets: http://localhost:9090/targets

**No data in Grafana:**
- Verify Prometheus is scraping (check targets)
- Generate traffic to create metrics
- Check data source in Grafana points to Prometheus
- Verify PromQL queries match actual metric names

**Grafana login issues:**
- Default credentials: admin / prom-operator
- Reset if needed: `kubectl get secret -n monitoring prometheus-grafana -o jsonpath="{.data.admin-password}" | base64 --decode`

### Cleanup

To remove the monitoring stack:

```bash
# Delete ServiceMonitor
kubectl delete -f k8s/servicemonitor.yaml

# Uninstall Prometheus/Grafana
helm uninstall prometheus -n monitoring

# Delete namespace
kubectl delete namespace monitoring
```

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
- **Prometheus**: Metrics collection and monitoring
- **Grafana**: Metrics visualization and dashboards
- **Helm**: Kubernetes package manager

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