# AIN3003 Bookstore Application

## Cloud-Native Bookstore with Azure Kubernetes Service

[![Azure](https://img.shields.io/badge/Azure-Kubernetes%20Service-blue)](https://azure.microsoft.com)
[![Python](https://img.shields.io/badge/Python-3.9-green)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.2.2-lightgrey)](https://flask.palletsprojects.com)
[![MongoDB](https://img.shields.io/badge/Database-Cosmos%20DB-green)](https://azure.microsoft.com/services/cosmos-db/)

A cloud-native bookstore web application deployed on Azure Kubernetes Service (AKS) with Azure Cosmos DB (MongoDB API) as the database backend.

---

## 📋 Project Overview

| Component | Technology |
|-----------|------------|
| **Backend** | Flask (Python 3.9) |
| **Database** | Azure Cosmos DB (MongoDB API) |
| **Container Registry** | Azure Container Registry (ACR) |
| **Orchestration** | Azure Kubernetes Service (AKS) |
| **Frontend** | HTML5, Bootstrap 4, Jinja2 |
| **Containerization** | Docker |

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   User/Client   │────▶│  Azure Load     │────▶│   AKS Cluster   │
│                 │     │  Balancer       │     │   (3 Replicas)  │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────┐
                                                │                 │
                                                │  Azure Cosmos   │
                                                │  DB (MongoDB)   │
                                                │                 │
                                                └─────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Azure CLI installed
- Docker installed
- kubectl installed
- Azure subscription

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/bookstore-project.git
cd bookstore-project
```

### 2. Azure Login

```bash
az login
```

### 3. Create Resource Group

```bash
az group create --name ain3003-bookstore-project --location northeurope
```

### 4. Create Azure Cosmos DB

```bash
az cosmosdb create \
  --name bookstore2202277 \
  --resource-group ain3003-bookstore-project \
  --kind MongoDB \
  --server-version 4.0 \
  --default-consistency-level Session \
  --capabilities EnableServerless
```

### 5. Create Azure Container Registry

```bash
az acr create \
  --resource-group ain3003-bookstore-project \
  --name bookstoreacr2026 \
  --sku Basic
```

### 6. Build and Push Docker Image

```bash
az acr login --name bookstoreacr2026

docker buildx build --platform linux/amd64 \
  -t bookstoreacr2026.azurecr.io/bookstore-app:v7 \
  --push .
```

### 7. Create AKS Cluster

```bash
az aks create \
  --resource-group ain3003-bookstore-project \
  --name bookstore-aks \
  --node-count 2 \
  --node-vm-size Standard_B2s_v2 \
  --attach-acr bookstoreacr2026 \
  --generate-ssh-keys
```

### 8. Get AKS Credentials

```bash
az aks get-credentials \
  --resource-group ain3003-bookstore-project \
  --name bookstore-aks
```

### 9. Deploy to Kubernetes

```bash
kubectl apply -f k8s/
```

### 10. Get External IP

```bash
kubectl get services
```

---

## 📁 Project Structure

```
bookstore-project/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container definition
├── bookstore.json        # Sample book data
├── templates/
│   └── index.html        # Web interface
└── k8s/
    ├── deployment.yaml   # Kubernetes Deployment
    ├── service.yaml      # LoadBalancer Service
    ├── configmap.yaml    # Application config
    ├── secret.yaml       # Database credentials
    ├── network-policy.yaml # Network rules
    └── pvc-mongo.yaml    # Persistent Volume Claim
```

---

## 🔌 REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Home page with book catalog |
| `GET` | `/books` | List all books |
| `GET` | `/books/<id>` | Get book by ID |
| `GET` | `/books/isbn/<isbn>` | Get book by ISBN |
| `POST` | `/books` | Add new book |
| `PUT` | `/books/<id>` | Update book by ID |
| `DELETE` | `/books/<id>` | Delete book by ID |
| `GET` | `/books/category/<category>` | Filter by category |
| `GET` | `/books/author/<name>` | Filter by author |
| `GET` | `/health` | Health check |
| `GET` | `/api` | API documentation |

---

## 📝 API Usage Examples

### Create a Book (POST)

```bash
curl -X POST http://31.69.420.42/books \
  -H "Content-Type: application/json" \
  -d '{
    "isbn": "1234567890",
    "title": "New Book",
    "year": 2024,
    "price": 29.99,
    "page": 300,
    "category": "IT",
    "publisher": {"id": 1, "name": "Publisher"},
    "author": {"firstName": "John", "lastName": "Doe"}
  }'
```

### Update a Book (PUT)

```bash
curl -X PUT http://31.69.420.42/books/<book_id> \
  -H "Content-Type: application/json" \
  -d '{"price": 24.99, "title": "Updated Title"}'
```

### Delete a Book (DELETE)

```bash
curl -X DELETE http://31.69.420.42/books/<book_id>
```

### Health Check

```bash
curl http://31.69.420.42/health
```

Response:
```json
{"status": "healthy", "database": "connected"}
```

---

## ⚙️ Kubernetes Commands

### Check Pod Status

```bash
kubectl get pods
```

### Check Services

```bash
kubectl get services
```

### View Logs

```bash
kubectl logs deployment/bookstore-app --tail=50
```

### Restart Deployment

```bash
kubectl rollout restart deployment/bookstore-app
```

### Scale Replicas

```bash
kubectl scale deployment/bookstore-app --replicas=5
```

---

## 💰 Cost Management

### Stop AKS Cluster (Save Money)

```bash
az aks stop --name bookstore-aks --resource-group ain3003-bookstore-project
```

### Start AKS Cluster

```bash
az aks start --name bookstore-aks --resource-group ain3003-bookstore-project
```

### Delete All Resources

```bash
az group delete --name ain3003-bookstore-project --yes
```

---

## 📊 Sample Data

The database contains 9 books across 2 categories:

**IT (7 books):**
- Head First HTML and CSS
- WebSocket
- Mastering JavaScript Design Patterns
- CSS3: The Missing Manual
- JavaScript Patterns
- Pro jQuery 2.0
- Java 8 in Action

**Science Fiction (2 books):**
- Dune
- The Hitchhiker's Guide to the Galaxy

---

## 🖼️ Screenshots

### Web Application
- Hero section with BAU library background
- Dynamic book catalog with cover images
- Real-time statistics from database
- Responsive Bootstrap design

### Features
- CRUD operations via REST API
- Book cover images from Open Library API
- Category filtering
- Health check endpoint for Kubernetes

---

## 👤 Author

**Can Kısacık**
- Student ID: 2202277
- University: Bahçeşehir University
- Department: Artificial Intelligence Engineering
- Course: AIN3003 - Database Systems and Cloud Computing

---

## 📄 License

This project was created for educational purposes as part of the AIN3003 course at Bahçeşehir University.

---

## 🙏 Acknowledgments

- Bahçeşehir University
- Microsoft Azure for Students
- Open Library Covers API
