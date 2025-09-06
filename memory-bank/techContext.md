# Technical Context: Suricata ML-IDS

## Technology Stack

### Core Technologies
- **Docker & Docker Compose**: Container orchestration
- **Suricata**: Network intrusion detection engine
- **Python 3.9+**: ML services development
- **OpenSearch**: Search and analytics engine
- **Redis**: Message queue and caching

### Python ML Stack
- **scikit-learn**: Machine learning algorithms
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **scapy**: Packet manipulation and analysis
- **asyncio**: Asynchronous programming

### Data Formats
- **PCAP**: Raw network packet captures
- **EVE JSON**: Suricata event format
- **CSV**: Feature datasets for ML training
- **Pickle**: Serialized Python ML models

## Development Environment

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- Python 3.9+ (for development)
- 8GB+ RAM (for OpenSearch)
- 20GB+ disk space

### Project Structure
```
suricata-ml-ids/
├── docker-compose.yml
├── services/
│   ├── suricata/
│   ├── feature-extractor/
│   ├── ml-trainer/
│   ├── realtime-detector/
│   ├── traffic-replay/
│   └── opensearch/
├── data/
│   ├── pcaps/
│   ├── models/
│   └── datasets/
├── scripts/
│   ├── demo.sh
│   └── setup.sh
└── docs/
```

## Service-Specific Technologies

### Suricata Service
- **Base Image**: suricata/suricata:latest
- **Configuration**: YAML-based rules and settings
- **Output**: EVE JSON format logs
- **Monitoring**: Built-in performance stats

### Feature Extractor
- **Base Image**: python:3.9-slim
- **Dependencies**: scapy, pandas, numpy
- **Input Processing**: PCAP parsing
- **Feature Engineering**: 25+ network features

### ML Trainer
- **Base Image**: python:3.9-slim
- **Dependencies**: scikit-learn, joblib
- **Algorithms**: Decision Tree, k-NN
- **Evaluation**: Cross-validation, metrics

### Real-time Detector
- **Base Image**: python:3.9-slim
- **Dependencies**: FastAPI, uvicorn
- **Architecture**: REST API + async processing
- **Models**: Ensemble predictions

### Traffic Replay
- **Base Image**: python:3.9-slim
- **Dependencies**: scapy, asyncio
- **Capabilities**: PCAP replay, synthetic generation
- **Control**: Rate limiting, scheduling

### OpenSearch
- **Base Image**: opensearchproject/opensearch:latest
- **Configuration**: JVM tuning, security settings
- **Dashboards**: Kibana-compatible visualizations
- **Data Ingestion**: Logstash/Beats patterns

## Development Workflows

### Local Development
1. Clone repository
2. Run `./scripts/setup.sh` for initial setup
3. Use `docker-compose up -d` for service startup
4. Access services via localhost ports

### Testing Pipeline
1. Unit tests for individual services
2. Integration tests for service communication
3. End-to-end tests with synthetic attack data
4. Performance benchmarking

### Deployment
1. Production: Docker Swarm or Kubernetes
2. Development: Docker Compose
3. CI/CD: GitHub Actions integration
4. Monitoring: Prometheus + Grafana

## Performance Considerations

### Resource Requirements
- **Suricata**: 2 CPU cores, 4GB RAM
- **OpenSearch**: 2 CPU cores, 4GB RAM
- **ML Services**: 1 CPU core, 2GB RAM each
- **Total**: 8 CPU cores, 16GB RAM minimum

### Optimization Strategies
- **Async Processing**: Non-blocking I/O operations
- **Batch Processing**: Efficient data processing
- **Model Caching**: In-memory model storage
- **Connection Pooling**: Database connections

### Monitoring Stack
- **Logging**: Structured JSON logs
- **Metrics**: Prometheus-compatible metrics
- **Tracing**: OpenTelemetry integration
- **Health Checks**: Docker health checks
