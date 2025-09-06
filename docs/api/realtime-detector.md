# Real-time Detector API Documentation

## Overview

The Real-time Detector service provides high-performance threat detection using trained machine learning models. It analyzes network features and returns predictions with sub-100ms latency using ensemble models.

**Base URL**: `http://localhost:8080`  
**Service**: `realtime-detector`  
**Port**: `8080`

## Authentication

Currently, no authentication is required for API access.

## Endpoints

### Health Check

#### `GET /health`

Check the health status of the Real-time Detector service.

**Response**

```json
{
  "status": "healthy",
  "service": "realtime-detector",
  "models_loaded": 3,
  "redis_status": "connected",
  "latency_target_ms": 100
}
```

**Status Codes**
- `200 OK` - Service is healthy
- `503 Service Unavailable` - Service is unhealthy

---

### Detect Threats

#### `POST /detect`

Analyze network features and return threat predictions using ensemble models.

**Request Body**

```json
{
  "features": {
    "total_packets": 150,
    "total_bytes": 15000,
    "avg_packet_size": 100.0,
    "duration": 5.0,
    "tcp_ratio": 0.8,
    "udp_ratio": 0.2,
    "icmp_ratio": 0.0,
    "packets_per_second": 30.0,
    "unique_src_ips": 2,
    "unique_dst_ips": 3,
    "tcp_syn_ratio": 0.6,
    "well_known_ports": 0.6,
    "high_ports": 0.4,
    "payload_entropy": 7.5,
    "fragmented_packets": 0.1,
    "suspicious_flags": 0.05,
    "http_requests": 10,
    "dns_queries": 5,
    "tls_handshakes": 3,
    "port_scan_indicators": 0.0,
    "ddos_indicators": 0.1,
    "malware_indicators": 0.0,
    "data_exfiltration_indicators": 0.0
  }
}
```

**Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `features` | object | Yes | Network feature vector (25+ features) |

**Example Request**

```bash
curl -X POST "http://localhost:8080/detect" \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "total_packets": 150,
      "total_bytes": 15000,
      "avg_packet_size": 100.0,
      "duration": 5.0,
      "tcp_ratio": 0.8,
      "udp_ratio": 0.2,
      "icmp_ratio": 0.0,
      "packets_per_second": 30.0,
      "unique_src_ips": 2,
      "unique_dst_ips": 3,
      "tcp_syn_ratio": 0.6,
      "well_known_ports": 0.6,
      "high_ports": 0.4,
      "payload_entropy": 7.5,
      "fragmented_packets": 0.1,
      "suspicious_flags": 0.05,
      "http_requests": 10,
      "dns_queries": 5,
      "tls_handshakes": 3
    }
  }'
```

**Normal Traffic Response**

```json
{
  "prediction": "normal",
  "confidence": 1.0,
  "threat_score": 0.0,
  "risk_level": "low",
  "model_predictions": {
    "predictions": {
      "decision_tree": "normal",
      "knn": "normal",
      "ensemble": "normal"
    },
    "confidences": {
      "decision_tree": 1.0,
      "knn": 1.0,
      "ensemble": 0.997
    },
    "probabilities": {
      "decision_tree": {"normal": 1.0, "attack": 0.0},
      "knn": {"normal": 1.0, "attack": 0.0},
      "ensemble": {"normal": 0.997, "attack": 0.003}
    }
  },
  "feature_analysis": {
    "anomaly_indicators": [],
    "suspicious_patterns": [],
    "risk_factors": []
  },
  "processing_time_ms": 89.3,
  "timestamp": 1757160337.34,
  "model_versions": {
    "decision_tree": "v1.0_20240115",
    "knn": "v1.0_20240115",
    "ensemble": "v1.0_20240115"
  }
}
```

**Attack Detection Response**

```json
{
  "prediction": "attack",
  "confidence": 0.95,
  "threat_score": 0.87,
  "risk_level": "high",
  "model_predictions": {
    "predictions": {
      "decision_tree": "attack",
      "knn": "attack",
      "ensemble": "attack"
    },
    "confidences": {
      "decision_tree": 0.92,
      "knn": 0.89,
      "ensemble": 0.95
    },
    "probabilities": {
      "decision_tree": {"normal": 0.08, "attack": 0.92},
      "knn": {"normal": 0.11, "attack": 0.89},
      "ensemble": {"normal": 0.05, "attack": 0.95}
    }
  },
  "feature_analysis": {
    "anomaly_indicators": [
      "high_packets_per_second",
      "suspicious_port_patterns",
      "unusual_payload_entropy"
    ],
    "suspicious_patterns": [
      "port_scan_detected",
      "ddos_indicators_present"
    ],
    "risk_factors": [
      "multiple_target_ips",
      "high_connection_rate",
      "abnormal_packet_sizes"
    ]
  },
  "processing_time_ms": 67.8,
  "timestamp": 1757160337.34,
  "model_versions": {
    "decision_tree": "v1.0_20240115",
    "knn": "v1.0_20240115",
    "ensemble": "v1.0_20240115"
  }
}
```

**Status Codes**
- `200 OK` - Prediction completed successfully
- `400 Bad Request` - Invalid feature data
- `503 Service Unavailable` - Models not loaded

---

### Batch Detection

#### `POST /detect/batch`

Analyze multiple feature vectors in a single request for improved throughput.

**Request Body**

```json
{
  "features_batch": [
    {
      "id": "flow_001",
      "features": {
        "total_packets": 150,
        "total_bytes": 15000,
        "avg_packet_size": 100.0
      }
    },
    {
      "id": "flow_002", 
      "features": {
        "total_packets": 300,
        "total_bytes": 45000,
        "avg_packet_size": 150.0
      }
    }
  ]
}
```

**Response**

```json
{
  "results": [
    {
      "id": "flow_001",
      "prediction": "normal",
      "confidence": 1.0,
      "threat_score": 0.0,
      "processing_time_ms": 45.2
    },
    {
      "id": "flow_002",
      "prediction": "attack",
      "confidence": 0.92,
      "threat_score": 0.78,
      "processing_time_ms": 43.1
    }
  ],
  "total_processed": 2,
  "batch_processing_time_ms": 88.3,
  "timestamp": 1757160337.34
}
```

---

### Model Status

#### `GET /models/status`

Get the current status of loaded models.

**Response**

```json
{
  "models_loaded": true,
  "model_info": {
    "decision_tree": {
      "loaded": true,
      "accuracy": 0.996,
      "load_time_ms": 45.2,
      "file": "synthetic_network_traffic_decision_tree_model.joblib",
      "version": "v1.0_20240115"
    },
    "knn": {
      "loaded": true,
      "accuracy": 0.996,
      "load_time_ms": 23.1,
      "file": "synthetic_network_traffic_knn_model.joblib",
      "version": "v1.0_20240115"
    },
    "ensemble": {
      "loaded": true,
      "accuracy": 1.0,
      "load_time_ms": 78.9,
      "file": "synthetic_network_traffic_ensemble_model.joblib",
      "version": "v1.0_20240115"
    }
  },
  "total_load_time_ms": 147.2,
  "last_updated": "2024-01-15T10:30:00Z"
}
```

---

### Reload Models

#### `POST /models/reload`

Reload models from disk (useful after retraining).

**Response**

```json
{
  "status": "success",
  "message": "Models reloaded successfully",
  "models_reloaded": 3,
  "reload_time_ms": 156.7,
  "timestamp": 1757160337.34
}
```

## Feature Schema

The Real-time Detector expects a complete feature vector with 25+ features:

### Required Features

| Feature | Type | Range | Description |
|---------|------|-------|-------------|
| `total_packets` | integer | 1+ | Total number of packets in flow |
| `total_bytes` | integer | 1+ | Total bytes transferred |
| `avg_packet_size` | float | 1.0+ | Average packet size in bytes |
| `duration` | float | 0.0+ | Flow duration in seconds |
| `tcp_ratio` | float | 0.0-1.0 | Ratio of TCP packets |
| `udp_ratio` | float | 0.0-1.0 | Ratio of UDP packets |
| `icmp_ratio` | float | 0.0-1.0 | Ratio of ICMP packets |
| `packets_per_second` | float | 0.0+ | Packet rate |
| `unique_src_ips` | integer | 1+ | Number of unique source IPs |
| `unique_dst_ips` | integer | 1+ | Number of unique destination IPs |
| `tcp_syn_ratio` | float | 0.0-1.0 | Ratio of TCP SYN packets |
| `well_known_ports` | float | 0.0-1.0 | Ratio of well-known ports |
| `high_ports` | float | 0.0-1.0 | Ratio of high ports |
| `payload_entropy` | float | 0.0-8.0 | Shannon entropy of payload |
| `fragmented_packets` | float | 0.0-1.0 | Ratio of fragmented packets |
| `suspicious_flags` | float | 0.0-1.0 | Ratio of suspicious TCP flags |
| `http_requests` | integer | 0+ | Number of HTTP requests |
| `dns_queries` | integer | 0+ | Number of DNS queries |
| `tls_handshakes` | integer | 0+ | Number of TLS handshakes |

### Optional Security Features

| Feature | Type | Range | Description |
|---------|------|-------|-------------|
| `port_scan_indicators` | float | 0.0-1.0 | Port scanning behavior score |
| `ddos_indicators` | float | 0.0-1.0 | DDoS attack indicators |
| `malware_indicators` | float | 0.0-1.0 | Malware communication patterns |
| `data_exfiltration_indicators` | float | 0.0-1.0 | Data exfiltration patterns |

### Feature Validation

The service validates:
- All required features are present
- Numeric values are within expected ranges
- Ratios sum to approximately 1.0 where applicable
- No NaN or infinite values

## Response Schema

### Prediction Response

| Field | Type | Description |
|-------|------|-------------|
| `prediction` | string | "normal", "attack", or "unknown" |
| `confidence` | float | Overall confidence score (0.0-1.0) |
| `threat_score` | float | Threat severity score (0.0-1.0) |
| `risk_level` | string | "low", "medium", "high", "critical" |
| `processing_time_ms` | float | Response time in milliseconds |
| `timestamp` | float | Unix timestamp of prediction |

### Model Predictions

| Field | Type | Description |
|-------|------|-------------|
| `predictions` | object | Individual model predictions |
| `confidences` | object | Individual model confidence scores |
| `probabilities` | object | Class probabilities for each model |

### Feature Analysis

| Field | Type | Description |
|-------|------|-------------|
| `anomaly_indicators` | array | List of detected anomalies |
| `suspicious_patterns` | array | Identified suspicious patterns |
| `risk_factors` | array | Contributing risk factors |

## Performance Specifications

### Latency Targets
- **Single Prediction**: <100ms (target), ~89ms (average)
- **Batch Prediction**: <50ms per item
- **Model Loading**: <200ms per model

### Throughput
- **Single Requests**: 1000+ requests/second
- **Batch Requests**: 5000+ features/second
- **Concurrent Connections**: Up to 100 simultaneous

### Resource Usage
- **Memory**: ~500MB (including loaded models)
- **CPU**: <50% per core under normal load
- **Storage**: Models cached in memory for fast access

## Error Handling

### Common Errors

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `MODELS_NOT_LOADED` | 503 | ML models are not loaded |
| `INVALID_FEATURES` | 400 | Feature data is invalid or incomplete |
| `FEATURE_OUT_OF_RANGE` | 400 | Feature values outside expected range |
| `PREDICTION_FAILED` | 500 | Error during model prediction |
| `REDIS_CONNECTION_ERROR` | 503 | Redis cache is unavailable |

### Error Response Format

```json
{
  "status": "error",
  "message": "Required feature 'total_packets' is missing",
  "error_code": "INVALID_FEATURES",
  "details": {
    "missing_features": ["total_packets", "total_bytes"],
    "provided_features": 23,
    "required_features": 25
  }
}
```

## Rate Limits

- **Detect Threats**: 1000 requests per minute
- **Batch Detection**: 100 requests per minute
- **Model Status**: 60 requests per minute
- **Health Check**: No limit

## Examples

### Python Client Example

```python
import requests
import json
import time

class ThreatDetector:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
    
    def detect_threat(self, features):
        """Detect threats in network features"""
        response = requests.post(
            f"{self.base_url}/detect",
            headers={"Content-Type": "application/json"},
            json={"features": features}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            error = response.json()
            raise Exception(f"Detection failed: {error['message']}")
    
    def batch_detect(self, features_list):
        """Batch threat detection"""
        batch_data = {
            "features_batch": [
                {"id": f"flow_{i}", "features": features}
                for i, features in enumerate(features_list)
            ]
        }
        
        response = requests.post(
            f"{self.base_url}/detect/batch",
            headers={"Content-Type": "application/json"},
            json=batch_data
        )
        
        return response.json()

# Usage example
detector = ThreatDetector()

# Single detection
features = {
    "total_packets": 150,
    "total_bytes": 15000,
    "avg_packet_size": 100.0,
    "duration": 5.0,
    "tcp_ratio": 0.8,
    "udp_ratio": 0.2,
    "icmp_ratio": 0.0,
    "packets_per_second": 30.0,
    "unique_src_ips": 2,
    "unique_dst_ips": 3,
    "tcp_syn_ratio": 0.6,
    "well_known_ports": 0.6,
    "high_ports": 0.4,
    "payload_entropy": 7.5,
    "fragmented_packets": 0.1,
    "suspicious_flags": 0.05,
    "http_requests": 10,
    "dns_queries": 5,
    "tls_handshakes": 3
}

result = detector.detect_threat(features)
print(f"Prediction: {result['prediction']}")
print(f"Confidence: {result['confidence']:.3f}")
print(f"Processing time: {result['processing_time_ms']:.1f}ms")

if result['prediction'] == 'attack':
    print("⚠️  THREAT DETECTED!")
    print(f"Risk level: {result['risk_level']}")
    print(f"Threat score: {result['threat_score']:.3f}")
```

### JavaScript Client Example

```javascript
class ThreatDetector {
  constructor(baseUrl = 'http://localhost:8080') {
    this.baseUrl = baseUrl;
  }
  
  async detectThreat(features) {
    try {
      const response = await fetch(`${this.baseUrl}/detect`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ features })
      });
      
      const result = await response.json();
      
      if (response.ok) {
        return result;
      } else {
        throw new Error(result.message);
      }
    } catch (error) {
      console.error('Threat detection failed:', error);
      throw error;
    }
  }
  
  async getModelStatus() {
    const response = await fetch(`${this.baseUrl}/models/status`);
    return response.json();
  }
}

// Usage
const detector = new ThreatDetector();

const features = {
  total_packets: 150,
  total_bytes: 15000,
  avg_packet_size: 100.0,
  duration: 5.0,
  tcp_ratio: 0.8,
  udp_ratio: 0.2,
  icmp_ratio: 0.0,
  packets_per_second: 30.0,
  unique_src_ips: 2,
  unique_dst_ips: 3,
  tcp_syn_ratio: 0.6,
  well_known_ports: 0.6,
  high_ports: 0.4,
  payload_entropy: 7.5,
  fragmented_packets: 0.1,
  suspicious_flags: 0.05,
  http_requests: 10,
  dns_queries: 5,
  tls_handshakes: 3
};

detector.detectThreat(features)
  .then(result => {
    console.log(`Prediction: ${result.prediction}`);
    console.log(`Confidence: ${result.confidence}`);
    console.log(`Processing time: ${result.processing_time_ms}ms`);
    
    if (result.prediction === 'attack') {
      console.warn('🚨 THREAT DETECTED!');
      console.log(`Risk level: ${result.risk_level}`);
    }
  })
  .catch(error => {
    console.error('Detection failed:', error);
  });
```

## Integration Notes

- The service automatically loads models from `/data/models/` directory
- Redis is used for caching and performance optimization
- Models can be hot-reloaded without service restart
- Feature vectors must match the training data schema
- The service provides detailed logging for debugging and monitoring
- WebSocket support available for real-time streaming detection
