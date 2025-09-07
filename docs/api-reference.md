# API Reference

Complete API documentation for all Suricata ML-IDS services.

## 📋 Service Overview

| Service | Port | Purpose | Health Check |
|---------|------|---------|--------------|
| **Feature Extractor** | 8001 | PCAP → CSV feature conversion | `GET /health` |
| **ML Trainer** | 8002 | Model training and evaluation | `GET /health` |
| **Real-time Detector** | 8080 | Live threat detection | `GET /health` |
| **Traffic Replay** | 8003 | Network simulation | `GET /health` |

---

## 🔍 Feature Extractor API (Port 8001)

### Extract Features from PCAP

**Endpoint:** `POST /extract`

**Purpose:** Convert network packet captures to ML-ready feature vectors

```bash
curl -X POST "http://localhost:8001/extract" \
     -H "Content-Type: application/json" \
     -d '{
       "pcap_file": "sample_traffic.pcap",
       "output_format": "csv",
       "feature_set": "full"
     }'
```

**Request Body:**
```json
{
  "pcap_file": "string",           // PCAP filename in /data/pcap/
  "output_format": "csv|json",     // Output format (default: csv)
  "feature_set": "basic|full",     // Feature complexity (default: full)
  "normalize": true,               // Normalize features (default: true)
  "include_metadata": false        // Include packet metadata (default: false)
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Features extracted successfully",
  "output_file": "sample_traffic_features.csv",
  "processing_time": 2.34,
  "statistics": {
    "total_packets": 1500,
    "processed_flows": 245,
    "features_extracted": 122,
    "file_size_mb": 0.8
  },
  "feature_summary": {
    "numerical_features": 81,
    "categorical_features": 41,
    "derived_features": 0
  }
}
```

### Health Check

**Endpoint:** `GET /health`

```bash
curl "http://localhost:8001/health"
```

**Response:**
```json
{
  "status": "healthy",
  "service": "feature-extractor",
  "version": "1.0.0",
  "uptime_seconds": 3600,
  "last_extraction": "2024-01-15T10:30:00Z"
}
```

---

## 🧠 ML Trainer API (Port 8002)

### Train Models

**Endpoint:** `POST /train`

**Purpose:** Train machine learning models on network traffic datasets

```bash
curl -X POST "http://localhost:8002/train" \
     -H "Content-Type: application/json" \
     -d '{
       "dataset_filename": "nsl_kdd_sample.csv",
       "algorithms": ["decision_tree", "knn", "ensemble"],
       "target_column": "label",
       "test_size": 0.2,
       "hyperparameters": {
         "decision_tree": {"max_depth": 15, "random_state": 42},
         "knn": {"n_neighbors": 7},
         "ensemble": {"n_estimators": 100, "random_state": 42}
       }
     }'
```

**Request Body:**
```json
{
  "dataset_filename": "string",    // CSV file in /data/datasets/
  "algorithms": ["string"],        // ["decision_tree", "knn", "ensemble"]
  "target_column": "string",       // Target column name (default: "label")
  "test_size": 0.2,               // Train/test split ratio
  "random_state": 42,             // Reproducibility seed
  "hyperparameters": {            // Algorithm-specific parameters
    "decision_tree": {
      "max_depth": 15,
      "min_samples_split": 2,
      "min_samples_leaf": 1,
      "random_state": 42
    },
    "knn": {
      "n_neighbors": 7,
      "weights": "uniform",
      "algorithm": "auto"
    },
    "ensemble": {
      "n_estimators": 100,
      "max_depth": 10,
      "random_state": 42
    }
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Models trained successfully",
  "training_id": "train_20240115_103045",
  "results": {
    "decision_tree": {
      "accuracy": 0.988,
      "precision": 0.985,
      "recall": 0.991,
      "f1_score": 0.988,
      "training_time": 1.2,
      "model_file": "decision_tree_20240115_103045.joblib"
    },
    "knn": {
      "accuracy": 0.989,
      "precision": 0.987,
      "recall": 0.992,
      "f1_score": 0.989,
      "training_time": 0.8,
      "model_file": "knn_20240115_103045.joblib"
    },
    "ensemble": {
      "accuracy": 0.992,
      "precision": 0.990,
      "recall": 0.994,
      "f1_score": 0.992,
      "training_time": 3.3,
      "model_file": "ensemble_20240115_103045.joblib"
    }
  },
  "best_model": "ensemble",
  "dataset_info": {
    "total_samples": 5000,
    "training_samples": 4000,
    "test_samples": 1000,
    "features": 122,
    "normal_samples": 4000,
    "attack_samples": 1000,
    "class_distribution": {
      "normal": 0.8,
      "attack": 0.2
    }
  },
  "confusion_matrix": {
    "true_positives": 198,
    "true_negatives": 794,
    "false_positives": 6,
    "false_negatives": 2
  }
}
```

### List Available Models

**Endpoint:** `GET /models`

```bash
curl "http://localhost:8002/models"
```

**Response:**
```json
{
  "status": "success",
  "models": [
    {
      "model_id": "ensemble_20240115_103045",
      "algorithm": "ensemble",
      "accuracy": 0.992,
      "created_at": "2024-01-15T10:30:45Z",
      "file_size_mb": 2.1,
      "training_samples": 4000
    },
    {
      "model_id": "decision_tree_20240115_103045", 
      "algorithm": "decision_tree",
      "accuracy": 0.988,
      "created_at": "2024-01-15T10:30:45Z",
      "file_size_mb": 0.3,
      "training_samples": 4000
    }
  ]
}
```

### Health Check

**Endpoint:** `GET /health`

```bash
curl "http://localhost:8002/health"
```

**Response:**
```json
{
  "status": "healthy",
  "service": "ml-trainer",
  "version": "1.0.0",
  "uptime_seconds": 3600,
  "models_trained": 15,
  "last_training": "2024-01-15T10:30:45Z"
}
```

---

## 🎯 Real-time Detector API (Port 8080)

### Detect Threats

**Endpoint:** `POST /detect`

**Purpose:** Real-time network threat detection using trained ML models

```bash
curl -X POST "http://localhost:8080/detect" \
     -H "Content-Type: application/json" \
     -d '{
       "features": [0, 1, 0, 0, 181, 5450, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 8, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 9, 9, 1.0, 0.0, 0.11, 0.0, 0.0, 0.0, 0.0, 0.0],
       "model_type": "ensemble"
     }'
```

**Request Body:**
```json
{
  "features": [float],             // 122-element feature vector
  "model_type": "string",          // "decision_tree", "knn", or "ensemble"
  "threshold": 0.5,                // Classification threshold (default: 0.5)
  "return_probabilities": true,    // Include prediction probabilities
  "session_id": "string"           // Optional session tracking
}
```

**Response:**
```json
{
  "prediction": "attack",          // "normal" or "attack"
  "confidence": 0.923,             // Prediction confidence (0-1)
  "probabilities": {
    "normal": 0.077,
    "attack": 0.923
  },
  "threat_score": 8.7,             // Threat severity (0-10)
  "processing_time_ms": 12,        // Detection latency
  "model_used": "ensemble",
  "model_version": "ensemble_20240115_103045",
  "timestamp": "2024-01-15T10:30:45Z",
  "session_id": "sess_abc123",
  "feature_importance": {          // Top contributing features
    "srv_count": 0.15,
    "count": 0.12,
    "serror_rate": 0.10
  }
}
```

### Batch Detection

**Endpoint:** `POST /detect/batch`

**Purpose:** Process multiple network flows simultaneously

```bash
curl -X POST "http://localhost:8080/detect/batch" \
     -H "Content-Type: application/json" \
     -d '{
       "samples": [
         {"features": [0, 1, 0, ...], "id": "flow_001"},
         {"features": [1, 0, 1, ...], "id": "flow_002"}
       ],
       "model_type": "ensemble"
     }'
```

**Request Body:**
```json
{
  "samples": [
    {
      "features": [float],         // 122-element feature vector
      "id": "string"               // Unique identifier for this sample
    }
  ],
  "model_type": "string",          // Model to use for all samples
  "threshold": 0.5
}
```

**Response:**
```json
{
  "status": "success",
  "results": [
    {
      "id": "flow_001",
      "prediction": "normal",
      "confidence": 0.856,
      "threat_score": 2.1
    },
    {
      "id": "flow_002", 
      "prediction": "attack",
      "confidence": 0.923,
      "threat_score": 8.7
    }
  ],
  "summary": {
    "total_samples": 2,
    "normal_predictions": 1,
    "attack_predictions": 1,
    "average_confidence": 0.889,
    "processing_time_ms": 18
  }
}
```

### Get Detection Statistics

**Endpoint:** `GET /stats`

```bash
curl "http://localhost:8080/stats"
```

**Response:**
```json
{
  "status": "success",
  "statistics": {
    "total_detections": 15420,
    "normal_detections": 13891,
    "attack_detections": 1529,
    "average_latency_ms": 14.2,
    "uptime_hours": 72.5,
    "detections_per_hour": 214,
    "model_performance": {
      "ensemble": {
        "usage_count": 12000,
        "average_confidence": 0.89,
        "average_latency_ms": 12.1
      },
      "decision_tree": {
        "usage_count": 2000,
        "average_confidence": 0.85,
        "average_latency_ms": 8.3
      }
    }
  }
}
```

### Health Check

**Endpoint:** `GET /health`

```bash
curl "http://localhost:8080/health"
```

**Response:**
```json
{
  "status": "healthy",
  "service": "realtime-detector",
  "version": "1.0.0",
  "uptime_seconds": 261000,
  "models_loaded": 3,
  "redis_connected": true,
  "elasticsearch_connected": true,
  "last_detection": "2024-01-15T10:30:45Z"
}
```

---

## 🚀 Traffic Replay API (Port 8003)

### Start Traffic Simulation

**Endpoint:** `POST /replay`

**Purpose:** Generate realistic network traffic for testing

```bash
curl -X POST "http://localhost:8003/replay" \
     -H "Content-Type: application/json" \
     -d '{
       "scenario": "mixed_traffic",
       "duration_seconds": 300,
       "packets_per_second": 100,
       "attack_ratio": 0.1
     }'
```

**Request Body:**
```json
{
  "scenario": "string",            // "normal", "attack", "mixed_traffic"
  "duration_seconds": 300,         // How long to generate traffic
  "packets_per_second": 100,       // Traffic intensity
  "attack_ratio": 0.1,            // Percentage of malicious traffic (0-1)
  "target_interface": "eth0",      // Network interface (default: auto)
  "protocols": ["tcp", "udp"],     // Protocols to simulate
  "attack_types": ["dos", "probe"] // Types of attacks to include
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Traffic replay started",
  "replay_id": "replay_20240115_103045",
  "configuration": {
    "scenario": "mixed_traffic",
    "duration_seconds": 300,
    "packets_per_second": 100,
    "estimated_packets": 30000,
    "attack_packets": 3000,
    "normal_packets": 27000
  },
  "start_time": "2024-01-15T10:30:45Z",
  "estimated_end_time": "2024-01-15T10:35:45Z"
}
```

### Stop Traffic Simulation

**Endpoint:** `POST /stop`

```bash
curl -X POST "http://localhost:8003/stop" \
     -H "Content-Type: application/json" \
     -d '{"replay_id": "replay_20240115_103045"}'
```

**Response:**
```json
{
  "status": "success",
  "message": "Traffic replay stopped",
  "replay_id": "replay_20240115_103045",
  "statistics": {
    "total_packets_sent": 15420,
    "normal_packets": 13878,
    "attack_packets": 1542,
    "duration_seconds": 154.2,
    "actual_pps": 100.1
  }
}
```

### Get Replay Status

**Endpoint:** `GET /status`

```bash
curl "http://localhost:8003/status"
```

**Response:**
```json
{
  "status": "success",
  "active_replays": [
    {
      "replay_id": "replay_20240115_103045",
      "scenario": "mixed_traffic",
      "start_time": "2024-01-15T10:30:45Z",
      "elapsed_seconds": 120,
      "remaining_seconds": 180,
      "packets_sent": 12000,
      "current_pps": 100.2
    }
  ],
  "service_status": "running"
}
```

### Health Check

**Endpoint:** `GET /health`

```bash
curl "http://localhost:8003/health"
```

**Response:**
```json
{
  "status": "healthy",
  "service": "traffic-replay",
  "version": "1.0.0",
  "uptime_seconds": 7200,
  "total_replays": 25,
  "active_replays": 1
}
```

---

## 🔧 Common Error Responses

### 400 Bad Request
```json
{
  "status": "error",
  "error_code": "INVALID_REQUEST",
  "message": "Missing required field: features",
  "details": {
    "field": "features",
    "expected_type": "array",
    "expected_length": 122
  }
}
```

### 404 Not Found
```json
{
  "status": "error",
  "error_code": "RESOURCE_NOT_FOUND", 
  "message": "Model not found: invalid_model_id",
  "available_models": ["ensemble_20240115_103045", "decision_tree_20240115_103045"]
}
```

### 500 Internal Server Error
```json
{
  "status": "error",
  "error_code": "INTERNAL_ERROR",
  "message": "Model prediction failed",
  "timestamp": "2024-01-15T10:30:45Z",
  "request_id": "req_abc123"
}
```

---

## 📊 Rate Limits

| Service | Endpoint | Limit | Window |
|---------|----------|-------|--------|
| **Feature Extractor** | `/extract` | 10 requests | 1 minute |
| **ML Trainer** | `/train` | 5 requests | 5 minutes |
| **Real-time Detector** | `/detect` | 1000 requests | 1 minute |
| **Real-time Detector** | `/detect/batch` | 100 requests | 1 minute |
| **Traffic Replay** | `/replay` | 3 requests | 1 minute |

---

## 🔐 Authentication

Currently, all APIs are open for development and testing. In production environments, implement:

- **API Keys**: Add `X-API-Key` header
- **JWT Tokens**: Bearer token authentication  
- **Rate Limiting**: Per-user quotas
- **IP Whitelisting**: Restrict access by source IP

---

## 🚀 Quick Start Examples

### Complete Detection Pipeline

```bash
# 1. Extract features from PCAP
curl -X POST "http://localhost:8001/extract" \
     -H "Content-Type: application/json" \
     -d '{"pcap_file": "sample.pcap"}'

# 2. Train models on extracted features  
curl -X POST "http://localhost:8002/train" \
     -H "Content-Type: application/json" \
     -d '{"dataset_filename": "sample_features.csv", "algorithms": ["ensemble"]}'

# 3. Detect threats in real-time
curl -X POST "http://localhost:8080/detect" \
     -H "Content-Type: application/json" \
     -d '{"features": [...], "model_type": "ensemble"}'
```

### Health Check All Services

```bash
#!/bin/bash
services=("8001" "8002" "8080" "8003")
for port in "${services[@]}"; do
  echo "Checking service on port $port..."
  curl -s "http://localhost:$port/health" | jq '.status'
done
```

---

## 📚 Related Documentation

- **[Machine Learning Guide](machine-learning-guide.md)** - ML concepts and algorithms
- **[Quick Start Guide](quick-start-guide.md)** - System setup and usage
- **[System Architecture](system-architecture.md)** - Technical architecture
- **[Performance Metrics](performance-metrics.md)** - Benchmarks and analysis
