# Project Brief: Suricata ML-IDS

## Project Overview
A comprehensive Intrusion Detection System (IDS) prototype combining signature-based detection (Suricata) with machine learning capabilities for cybersecurity education and research.

## Core Requirements

### Architecture Components
1. **Suricata IDS** - Signature-based network intrusion detection
2. **Python Feature Extractor** - PCAP to 25+ CSV features conversion
3. **ML Trainer** - Decision Tree + k-NN comparison training
4. **Real-time Detector** - Ensemble predictions for live detection
5. **OpenSearch** - SIEM visualization and log management
6. **Traffic Replay** - Testing simulation with synthetic attack data

### Performance Targets
- **ML Accuracy**: >90% on test data
- **Latency**: <100ms for real-time detection
- **Deployment**: One-command deployment via `./demo.sh demo`

### Deliverables
- docker-compose.yml with 6 services
- 3 Python ML services using scikit-learn
- Setup/demo automation scripts
- Synthetic attack data generation
- OpenSearch dashboards for monitoring
- Complete documentation + architecture diagrams

### Use Case
- Academic research focus for CS coursework
- Production-ready Docker architecture
- Cybersecurity education and research demonstration

## Success Criteria
Complete package ready for immediate deployment and educational use with comprehensive monitoring, high accuracy ML detection, and real-time performance.
