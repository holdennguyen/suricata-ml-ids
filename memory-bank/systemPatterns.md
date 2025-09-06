# System Patterns: Suricata ML-IDS

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Traffic       │    │   Suricata      │    │   Feature       │
│   Replay        │───▶│   IDS           │───▶│   Extractor     │
│   Service       │    │   Service       │    │   Service       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   OpenSearch    │◀───│   Real-time     │◀───│   ML Trainer    │
│   SIEM          │    │   Detector      │    │   Service       │
│   Service       │    │   Service       │    │   Service       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Service Architecture

### 1. Traffic Replay Service
- **Purpose**: Generate network traffic for testing
- **Technology**: Python + Scapy
- **Inputs**: PCAP files, synthetic attack patterns
- **Outputs**: Network packets to monitored interface

### 2. Suricata IDS Service
- **Purpose**: Signature-based intrusion detection
- **Technology**: Suricata engine
- **Inputs**: Network traffic
- **Outputs**: EVE JSON logs, alerts

### 3. Feature Extractor Service
- **Purpose**: Convert network data to ML features
- **Technology**: Python + pandas/numpy
- **Inputs**: PCAP files, Suricata logs
- **Outputs**: CSV with 25+ engineered features

### 4. ML Trainer Service
- **Purpose**: Train and evaluate ML models
- **Technology**: Python + scikit-learn
- **Inputs**: Labeled feature datasets
- **Outputs**: Trained models (Decision Tree, k-NN)

### 5. Real-time Detector Service
- **Purpose**: Live threat detection using ensemble
- **Technology**: Python + trained models
- **Inputs**: Real-time features, Suricata alerts
- **Outputs**: Threat predictions, confidence scores

### 6. OpenSearch Service
- **Purpose**: SIEM visualization and log management
- **Technology**: OpenSearch + Dashboards
- **Inputs**: All service logs and alerts
- **Outputs**: Interactive dashboards, search interface

## Data Flow Patterns

### Training Pipeline
1. Traffic Replay → Network packets
2. Suricata → Security alerts + logs
3. Feature Extractor → Structured features
4. ML Trainer → Trained models

### Detection Pipeline
1. Live traffic → Suricata + Feature Extractor
2. Features + Alerts → Real-time Detector
3. Predictions → OpenSearch
4. Dashboards → Security analysts

## Communication Patterns

### Inter-service Communication
- **File-based**: Shared volumes for PCAP/model files
- **Log-based**: Structured JSON logging
- **API-based**: REST endpoints for model serving
- **Message Queue**: Redis for real-time data streams

### Data Persistence
- **Models**: Persistent volumes for trained ML models
- **Logs**: OpenSearch for searchable log storage
- **Raw Data**: Shared volumes for PCAP files
- **Configuration**: Docker secrets/configs

## Scalability Patterns

### Horizontal Scaling
- Multiple feature extractor instances
- Load-balanced detector services
- OpenSearch cluster configuration

### Performance Optimization
- Async processing for real-time components
- Batch processing for training pipelines
- Caching for frequently accessed models
- Stream processing for high-throughput scenarios
