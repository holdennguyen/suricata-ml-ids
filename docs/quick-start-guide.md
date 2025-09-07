# Quick Start Guide

## 🚀 Getting Started

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- Python 3.9+ (for ML scripts and utilities)
- 8GB+ RAM (for Elasticsearch)
- 20GB+ disk space

### 🎯 One-Command Complete Demo
```bash
# Clone repository and run complete demonstration
git clone <repository-url>
cd suricata-ml-ids

# Setup Python virtual environment (required for ML scripts)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Setup and start everything
./scripts/setup.sh
./scripts/demo.sh demo
```

**What this does:**
- Starts all 9 services (Suricata, ML pipeline, Elasticsearch, Kibana, etc.)
- Trains ML models with 99.2% accuracy on NSL-KDD dataset
- Demonstrates real-time threat detection (<30ms response)
- Creates sample alerts and ML detections in Elasticsearch
- Provides access to Kibana dashboards with working time filters

### 📋 Step-by-Step Demo Commands

#### 1. **System Management**
```bash
# Start all services
./scripts/demo.sh start

# Check service health (all 9 services)
./scripts/demo.sh status

# View logs for specific service
./scripts/demo.sh logs [service-name]

# Stop all services
./scripts/demo.sh stop

# Clean restart
./scripts/demo.sh restart
```

#### 2. **Individual Demonstrations**

**🧠 ML Training Demo** - Train ensemble models with NSL-KDD dataset
```bash
./scripts/demo.sh demo-ml
```
- Trains Decision Tree, k-NN, and Ensemble models on NSL-KDD data
- Achieves 99.2% accuracy with ensemble model (real-world benchmark)
- Uses industry-standard NSL-KDD intrusion detection dataset
- Saves models for real-time detection
- Training time: ~5 seconds

**⚡ Real-time Detection Demo** - Test threat detection API
```bash
./scripts/demo.sh demo-detection
```
- Tests normal vs attack traffic patterns
- Response time: 8-29ms (target: <100ms)
- Creates sample Suricata alerts
- Sends ML predictions to Elasticsearch

**🔧 Feature Extraction Demo** - Extract network features from PCAP
```bash
./scripts/demo.sh demo-extraction
```
- Processes PCAP files into 122+ features
- Demonstrates feature engineering pipeline
- Creates datasets for ML training

#### 3. **System Cleanup**
```bash
# Stop services and optionally remove data
./scripts/demo.sh cleanup
```

### 🌐 Access Points After Demo

| Service | URL | Purpose |
|---------|-----|---------|
| **Kibana SIEM** | http://localhost:5601 | Security dashboards and log analysis |
| **Real-time API** | http://localhost:8080/docs | ML threat detection API |
| **ML Trainer** | http://localhost:8002/docs | Model training and evaluation |
| **Feature Extractor** | http://localhost:8001/docs | PCAP feature extraction |
| **Traffic Replay** | http://localhost:8003/docs | Network simulation |
| **Elasticsearch** | http://localhost:9200 | Raw data access |

### 📊 Expected Demo Results

**Performance Metrics:**
- ML Accuracy: 99.2% (Ensemble model on NSL-KDD dataset)
- Detection Latency: 8-29ms
- Log Processing: 2000+ events/session
- System Health: 9/9 services operational

**Data Generated:**
- Suricata Events: 2000+ real-time network logs
- Security Alerts: 5+ signature-based detections  
- ML Detections: 6+ machine learning predictions
- All with current timestamps for Kibana time filters

## 🛠️ Development Guide

### Smart Rebuild System
```bash
# Rebuild specific service with cache-busting
./scripts/dev-rebuild.sh ml-trainer

# Rebuild all services
./scripts/dev-rebuild.sh all

# Force clean rebuild (for persistent issues)
./scripts/dev-rebuild.sh all force-clean
```

### Development Workflow
1. **Make Code Changes**: Edit source files in `services/*/src/`
2. **Rebuild Service**: Use `dev-rebuild.sh` for the specific service
3. **Test Changes**: Run individual demos or full system test
4. **Check Health**: Verify all services remain healthy

### Key Features
- **Intelligent Caching**: Only rebuilds changed Docker layers
- **Health Verification**: Automatically tests rebuilt services
- **Fast Rebuilds**: Only rebuilds changed layers
- **Health Verification**: Ensures services start correctly

## 🎓 Educational Features

### ML Pipeline
- **NSL-KDD Dataset**: Industry-standard benchmark with 148K samples
- **122 Network Features**: Comprehensive real-world traffic analysis
- **Ensemble Models**: Decision Tree + k-NN achieving 99.2% accuracy
- **Performance Metrics**: Exceeds 90% target with 99.2% on real data
- **Feature Importance**: Explainable AI insights from actual attack patterns

### Real-time Detection
- **Sub-30ms Latency**: Production-ready performance (8-29ms measured)
- **Ensemble Predictions**: Combines Decision Tree, k-NN, and Ensemble models
- **Confidence Scoring**: Probabilistic predictions with threat scores
- **String Labels**: Returns "normal", "attack", or "unknown" predictions
- **Model Loading**: Automatically loads trained models from ML Trainer

### SIEM Integration
- **Real-time Dashboards**: Live security monitoring via Kibana
- **Log Correlation**: Combines Suricata alerts with ML predictions
- **Historical Analysis**: Search and analyze past security events
- **Custom Visualizations**: Create domain-specific security dashboards

## 🏥 Monitoring & Health Checks

### Service Status
```bash
# Check all services
./scripts/demo.sh status

# Expected output: 9/9 services healthy
```

### Individual Service Health
- **Feature Extractor**: `curl http://localhost:8001/health`
- **ML Trainer**: `curl http://localhost:8002/health`
- **Real-time Detector**: `curl http://localhost:8080/health`
- **Traffic Replay**: `curl http://localhost:8003/health`
- **Elasticsearch**: `curl http://localhost:9200/_cluster/health`
- **Kibana**: `curl http://localhost:5601/api/status`

### Troubleshooting

**Common Issues:**
1. **Port conflicts**: Ensure ports 5601, 8001-8003, 8080, 9200, 6379 are free
2. **Memory issues**: Elasticsearch requires 8GB+ RAM
3. **Docker issues**: Restart Docker service if containers fail to start

**Solutions:**
```bash
# Check port usage
netstat -tulpn | grep :9200

# Free up memory
docker system prune -f

# Restart specific service
docker-compose restart elasticsearch
```

## 🔄 Using Custom Datasets

### Quick Custom Dataset Setup

If you want to use your own dataset instead of NSL-KDD:

#### 1. **Prepare Your Dataset**
```bash
# Option A: Use the preprocessing template
python3 data/custom_dataset_template.py

# Option B: Manual preparation
# Ensure your CSV has:
# - A 'label' column with 'normal' and 'attack' values
# - Numerical feature columns
# - No missing values
cp your_dataset.csv data/datasets/custom_dataset.csv
```

#### 2. **Test Your Dataset**
```bash
# Start services
./scripts/demo.sh start

# Test training with your dataset
curl -X POST "http://localhost:8002/train" \
     -H "Content-Type: application/json" \
     -d '{
       "dataset_filename": "custom_dataset.csv",
       "algorithms": ["decision_tree"],
       "target_column": "label",
       "test_size": 0.2
     }'
```

#### 3. **Update Demo Script (Optional)**
```bash
# Edit scripts/demo.sh
# In demo_ml_training function, change:
# "dataset_filename": "nsl_kdd_sample.csv"
# to:
# "dataset_filename": "custom_dataset.csv"

# Run full demo with your dataset
./scripts/demo.sh demo
```

### Dataset Requirements

Your CSV file must have:
- **Label column**: Named `label` with values `normal` or `attack`
- **Feature columns**: Numerical values (categorical will be auto-encoded)
- **Minimum size**: 1000+ samples recommended
- **Format**: CSV with headers

**Example format:**
```csv
feature1,feature2,feature3,label
1.5,0.8,2.1,normal
0.2,1.9,0.5,attack
2.1,0.3,1.8,normal
```

For detailed instructions, see: **[Machine Learning Guide - Custom Datasets](machine-learning-guide.md#-using-custom-datasets)**

---

## 📚 Next Steps

### For Beginners
- Read [Machine Learning Guide](machine-learning-guide.md)
- Explore [API Documentation](api-reference.md)
- Try modifying ML parameters in the training API

### For Developers
- Review [System Architecture](system-architecture.md)
- Check custom dataset preprocessing examples
- Explore service source code in `services/*/src/`

### For Security Professionals
- Configure Kibana Dashboards for your data
- Integrate with existing SIEM systems
- Customize Suricata rules for your environment
