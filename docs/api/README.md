# Suricata ML-IDS API Documentation

## Overview

This directory contains comprehensive API documentation for all services in the Suricata ML-IDS system. Each service provides RESTful APIs for integration and automation.

## Services

### 🔍 [Feature Extractor API](feature-extractor.md)
**Port**: 8001  
**Purpose**: Extract network features from PCAP files for ML analysis

Key endpoints:
- `POST /extract` - Extract features from PCAP files
- `POST /batch-extract` - Batch feature extraction
- `GET /health` - Service health check

### 🧠 [ML Trainer API](ml-trainer.md)
**Port**: 8002  
**Purpose**: Train machine learning models for intrusion detection

Key endpoints:
- `POST /train` - Train Decision Tree, k-NN, and Ensemble models
- `POST /evaluate` - Evaluate trained models
- `GET /models` - List available models
- `GET /models/{model_name}` - Get model details

### 🚨 [Real-time Detector API](realtime-detector.md)
**Port**: 8080  
**Purpose**: High-performance real-time threat detection

Key endpoints:
- `POST /detect` - Single threat detection (<100ms)
- `POST /detect/batch` - Batch threat detection
- `GET /models/status` - Model loading status
- `POST /models/reload` - Reload models

### 🔄 [Traffic Replay API](traffic-replay.md)
**Port**: 8003  
**Purpose**: Network traffic simulation and replay

Key endpoints:
- `POST /replay` - Replay PCAP files
- `POST /generate` - Generate synthetic traffic
- `GET /pcaps` - List available PCAP files
- `GET /replay/{id}/status` - Replay status

### 📡 Log Shipper Service
**Port**: Internal  
**Purpose**: Real-time streaming of eve.json logs to Elasticsearch

Features:
- Real-time file monitoring and processing
- Direct Elasticsearch integration
- Automatic index management
- Production-ready log ingestion pipeline

## Quick Start

### Prerequisites
- All services running via `docker-compose up -d`
- Services healthy (check with `./scripts/demo.sh status`)

### Basic Usage

```bash
# Check all services are healthy
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8080/health
curl http://localhost:8003/health

# Extract features from PCAP
curl -X POST "http://localhost:8001/extract" \
  -H "Content-Type: application/json" \
  -d '{"pcap_filename": "demo_traffic.pcap"}'

# Train ML models
curl -X POST "http://localhost:8002/train" \
  -H "Content-Type: application/json" \
  -d '{"dataset_filename": "synthetic_network_traffic.csv"}'

# Detect threats in real-time
curl -X POST "http://localhost:8080/detect" \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "total_packets": 150,
      "total_bytes": 15000,
      "avg_packet_size": 100.0,
      "duration": 5.0,
      "tcp_ratio": 0.8,
      "udp_ratio": 0.2
    }
  }'
```

## API Standards

### Response Format
All APIs follow consistent response patterns:

**Success Response**:
```json
{
  "status": "success",
  "message": "Operation completed successfully",
  "data": { ... },
  "processing_time_ms": 123.45,
  "timestamp": 1757160337.34
}
```

**Error Response**:
```json
{
  "status": "error",
  "message": "Human-readable error description",
  "error_code": "MACHINE_READABLE_CODE",
  "details": { ... }
}
```

### HTTP Status Codes
- `200 OK` - Request successful
- `400 Bad Request` - Invalid request parameters
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service unhealthy

### Content Types
- Request: `application/json`
- Response: `application/json`
- Health checks: `application/json`

## Authentication

Currently, all APIs operate without authentication for development and testing. For production deployments, consider implementing:

- API key authentication
- JWT tokens
- Rate limiting
- IP whitelisting

## Rate Limiting

Each service implements rate limiting to prevent abuse:

| Service | Endpoint | Limit |
|---------|----------|-------|
| Feature Extractor | `/extract` | 10/min |
| ML Trainer | `/train` | 5/hour |
| Real-time Detector | `/detect` | 1000/min |
| Traffic Replay | `/replay` | 10/hour |

## Performance Targets

| Service | Target Latency | Throughput |
|---------|----------------|------------|
| Feature Extractor | <1s per 1000 packets | 10 files/min |
| ML Trainer | <2s per model | 5 trainings/hour |
| Real-time Detector | <100ms | 1000+ req/sec |
| Traffic Replay | Real-time | 10K packets/sec |

## Error Handling

### Common Error Patterns

1. **File Not Found**: Check file paths and permissions
2. **Invalid Data**: Validate input schemas
3. **Service Unavailable**: Check service health
4. **Rate Limited**: Implement backoff strategies

### Retry Strategies

```python
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session_with_retries():
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session
```

## Integration Examples

### Python SDK Example

```python
import requests
import json

class MLIDSClient:
    def __init__(self, base_url="http://localhost"):
        self.feature_extractor = f"{base_url}:8001"
        self.ml_trainer = f"{base_url}:8002"
        self.detector = f"{base_url}:8080"
        self.replay = f"{base_url}:8003"
    
    def extract_features(self, pcap_file):
        response = requests.post(
            f"{self.feature_extractor}/extract",
            json={"pcap_filename": pcap_file}
        )
        return response.json()
    
    def train_models(self, dataset_file):
        response = requests.post(
            f"{self.ml_trainer}/train",
            json={"dataset_filename": dataset_file}
        )
        return response.json()
    
    def detect_threat(self, features):
        response = requests.post(
            f"{self.detector}/detect",
            json={"features": features}
        )
        return response.json()

# Usage
client = MLIDSClient()
result = client.detect_threat({
    "total_packets": 150,
    "tcp_ratio": 0.8,
    "payload_entropy": 7.5
})
print(f"Threat detected: {result['prediction']}")
```

### JavaScript SDK Example

```javascript
class MLIDSClient {
  constructor(baseUrl = 'http://localhost') {
    this.endpoints = {
      featureExtractor: `${baseUrl}:8001`,
      mlTrainer: `${baseUrl}:8002`,
      detector: `${baseUrl}:8080`,
      replay: `${baseUrl}:8003`
    };
  }
  
  async extractFeatures(pcapFile) {
    const response = await fetch(`${this.endpoints.featureExtractor}/extract`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pcap_filename: pcapFile })
    });
    return response.json();
  }
  
  async detectThreat(features) {
    const response = await fetch(`${this.endpoints.detector}/detect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ features })
    });
    return response.json();
  }
}

// Usage
const client = new MLIDSClient();
const result = await client.detectThreat({
  total_packets: 150,
  tcp_ratio: 0.8,
  payload_entropy: 7.5
});
console.log(`Prediction: ${result.prediction}`);
```

## Monitoring and Logging

### Health Monitoring

Monitor all services with a simple health check script:

```bash
#!/bin/bash
services=("8001" "8002" "8080" "8003")
for port in "${services[@]}"; do
  status=$(curl -s "http://localhost:$port/health" | jq -r '.status')
  echo "Service on port $port: $status"
done
```

### Log Aggregation

Services log to stdout/stderr for Docker log collection:

```bash
# View logs for specific service
docker-compose logs -f feature-extractor

# View all service logs
docker-compose logs -f

# Export logs for analysis
docker-compose logs --no-color > ids-logs.txt
```

## Development

### API Testing

Use the provided test scripts:

```bash
# Test all APIs
./scripts/test-apis.sh

# Test specific service
curl -X POST "http://localhost:8080/detect" \
  -H "Content-Type: application/json" \
  -d @test-data/sample-features.json
```

### Adding New Endpoints

1. Update service code with new endpoint
2. Add endpoint documentation to service API file
3. Update this README with endpoint summary
4. Add integration tests
5. Update client SDKs

## Support

For API support and questions:

1. Check service health endpoints
2. Review error messages and codes
3. Consult individual service documentation
4. Check Docker container logs
5. Verify network connectivity between services

## Changelog

### v1.0.0 (2025-09-06)
- Initial API documentation
- Feature Extractor API v1.0
- ML Trainer API v1.0
- Real-time Detector API v1.0
- Traffic Replay API v1.0
- Comprehensive examples and integration guides
