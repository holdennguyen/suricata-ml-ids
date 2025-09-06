#!/bin/bash

# Demo script for Suricata ML-IDS
# Provides one-command deployment and demonstration scenarios

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_demo() {
    echo -e "${PURPLE}[DEMO]${NC} $1"
}

# Detect Docker Compose command
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    print_error "Docker Compose is not available"
    exit 1
fi

# Function to check if services are healthy
check_services_health() {
    print_status "Checking service health..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        print_status "Health check attempt $attempt/$max_attempts"
        
        # Check individual services
        local healthy_services=0
        local total_services=6
        
        # Check feature-extractor
        if curl -f -s http://localhost:8001/health > /dev/null 2>&1; then
            ((healthy_services++))
        fi
        
        # Check ml-trainer
        if curl -f -s http://localhost:8002/health > /dev/null 2>&1; then
            ((healthy_services++))
        fi
        
        # Check realtime-detector
        if curl -f -s http://localhost:8080/health > /dev/null 2>&1; then
            ((healthy_services++))
        fi
        
        # Check OpenSearch
        if curl -f -s http://localhost:9200/_cluster/health > /dev/null 2>&1; then
            ((healthy_services++))
        fi
        
        # Check OpenSearch Dashboards
        if curl -f -s http://localhost:5601/api/status > /dev/null 2>&1; then
            ((healthy_services++))
        fi
        
        # Check Redis
        if redis-cli -h localhost -p 6379 ping > /dev/null 2>&1; then
            ((healthy_services++))
        fi
        
        print_status "Healthy services: $healthy_services/$total_services"
        
        if [ $healthy_services -eq $total_services ]; then
            print_success "All services are healthy!"
            return 0
        fi
        
        sleep 10
        ((attempt++))
    done
    
    print_warning "Not all services are healthy, but proceeding with demo..."
    return 1
}

# Function to start all services
start_services() {
    print_status "Starting Suricata ML-IDS services..."
    
    # Start services in dependency order
    $COMPOSE_CMD up -d redis elasticsearch
    
    print_status "Waiting for core services to initialize..."
    sleep 20
    
    # Start remaining services
    $COMPOSE_CMD up -d kibana suricata feature-extractor ml-trainer realtime-detector traffic-replay
    
    print_status "Waiting for all services to start..."
    sleep 30
    
    print_success "All services started!"
    
    # Show service status
    $COMPOSE_CMD ps
    
    # Check health
    check_services_health
}

# Function to stop all services
stop_services() {
    print_status "Stopping Suricata ML-IDS services..."
    
    $COMPOSE_CMD down
    
    print_success "All services stopped!"
}

# Function to restart all services
restart_services() {
    print_status "Restarting Suricata ML-IDS services..."
    
    stop_services
    sleep 5
    start_services
}

# Function to show service logs
show_logs() {
    local service=${1:-}
    
    if [ -z "$service" ]; then
        print_status "Showing logs for all services..."
        $COMPOSE_CMD logs -f
    else
        print_status "Showing logs for service: $service"
        $COMPOSE_CMD logs -f "$service"
    fi
}

# Function to run ML training demo
demo_ml_training() {
    print_demo "Running ML Training Demo..."
    
    # Check if synthetic data exists
    if [ ! -f "data/datasets/synthetic_network_traffic.csv" ]; then
        print_warning "Synthetic data not found. Generating..."
        (cd data && python3 generate_synthetic_data.py)
    fi
    
    # Train models using API
    print_demo "Training Decision Tree and k-NN models..."
    
    curl -X POST "http://localhost:8002/train" \
         -H "Content-Type: application/json" \
         -d '{
           "dataset_filename": "synthetic_network_traffic.csv",
           "algorithms": ["decision_tree", "knn", "ensemble"],
           "target_column": "label",
           "test_size": 0.2,
           "hyperparameters": {
             "decision_tree": {"max_depth": [20]},
             "knn": {"n_neighbors": [5]}
           }
         }' | jq '.'
    
    print_success "ML training demo completed!"
}

# Function to run real-time detection demo
demo_realtime_detection() {
    print_demo "Running Real-time Detection Demo..."
    
    # Test individual detection
    print_demo "Testing normal traffic detection..."
    
    curl -X POST "http://localhost:8080/detect" \
         -H "Content-Type: application/json" \
         -d '{
           "features": {
             "total_packets": 45.0,
             "total_bytes": 4800.0,
             "avg_packet_size": 106.7,
             "tcp_ratio": 0.8,
             "udp_ratio": 0.15,
             "icmp_ratio": 0.05,
             "packets_per_second": 8.5,
             "unique_src_ips": 2.0,
             "unique_dst_ips": 3.0,
             "tcp_syn_ratio": 0.2,
             "well_known_ports": 5.0,
             "payload_entropy": 6.2,
             "suspicious_flags": 0.0,
             "http_requests": 4.0,
             "dns_queries": 2.0,
             "tls_handshakes": 1.0
           },
           "source_ip": "192.168.1.100"
         }' | jq '.'
    
    print_demo "Testing attack traffic detection..."
    
    curl -X POST "http://localhost:8080/detect" \
         -H "Content-Type: application/json" \
         -d '{
           "features": {
             "total_packets": 250.0,
             "total_bytes": 15000.0,
             "avg_packet_size": 60.0,
             "tcp_ratio": 0.95,
             "udp_ratio": 0.05,
             "icmp_ratio": 0.0,
             "packets_per_second": 50.0,
             "unique_src_ips": 1.0,
             "unique_dst_ips": 25.0,
             "tcp_syn_ratio": 0.9,
             "well_known_ports": 20.0,
             "payload_entropy": 3.0,
             "suspicious_flags": 8.0,
             "http_requests": 0.0,
             "dns_queries": 0.0,
             "tls_handshakes": 0.0
           },
           "source_ip": "10.0.0.100"
         }' | jq '.'
    
    print_success "Real-time detection demo completed!"
}

# Function to run feature extraction demo
demo_feature_extraction() {
    print_demo "Running Feature Extraction Demo..."
    
    # Check if sample PCAP files exist
    if [ ! -d "data/pcaps/samples" ] || [ -z "$(ls -A data/pcaps/samples)" ]; then
        print_warning "No sample PCAP files found. Creating synthetic PCAP..."
        
        # Create a simple synthetic PCAP using Python and Scapy
        cat > data/create_sample_pcap.py << 'EOF'
#!/usr/bin/env python3
import os
os.environ['SCAPY_USE_PCAPY'] = '0'

from scapy.all import *
from scapy.layers.inet import IP, TCP, UDP, ICMP
import random

def create_sample_pcap():
    packets = []
    
    # Generate normal HTTP traffic
    for i in range(50):
        pkt = IP(src=f"192.168.1.{random.randint(10, 50)}", 
                dst="93.184.216.34") / TCP(sport=random.randint(32768, 65535), 
                                          dport=80) / "GET / HTTP/1.1\r\nHost: example.com\r\n\r\n"
        packets.append(pkt)
    
    # Generate DNS queries
    for i in range(20):
        pkt = IP(src=f"192.168.1.{random.randint(10, 50)}", 
                dst="8.8.8.8") / UDP(sport=random.randint(32768, 65535), 
                                    dport=53) / "DNS Query"
        packets.append(pkt)
    
    # Generate suspicious port scan
    src_ip = "10.0.0.100"
    for port in range(20, 100, 5):
        pkt = IP(src=src_ip, dst="192.168.1.10") / TCP(sport=54321, dport=port, flags="S")
        packets.append(pkt)
    
    # Save to PCAP file
    wrpcap('pcaps/samples/demo_traffic.pcap', packets)
    print(f"Created sample PCAP with {len(packets)} packets")

if __name__ == "__main__":
    create_sample_pcap()
EOF
        
        cd data && python3 create_sample_pcap.py && cd ..
    fi
    
    # Extract features from PCAP
    print_demo "Extracting features from sample PCAP..."
    
    curl -X POST "http://localhost:8001/extract" \
         -H "Content-Type: application/json" \
         -d '{
           "pcap_filename": "demo_traffic.pcap",
           "include_payload": true,
           "output_format": "csv"
         }' | jq '.'
    
    print_success "Feature extraction demo completed!"
}

# Function to show service status
show_status() {
    print_status "Suricata ML-IDS Service Status:"
    echo
    
    $COMPOSE_CMD ps
    echo
    
    print_status "Service Health Checks:"
    
    # Check each service
    services=(
        "feature-extractor:8001:/health"
        "ml-trainer:8002:/health"
        "realtime-detector:8080:/health"
        "elasticsearch:9200:/_cluster/health"
        "kibana:5601:/api/status"
    )
    
    for service_info in "${services[@]}"; do
        IFS=':' read -r service port endpoint <<< "$service_info"
        
        if curl -f -s "http://localhost:$port$endpoint" > /dev/null 2>&1; then
            print_success "$service is healthy"
        else
            print_error "$service is not responding"
        fi
    done
    
    # Check Redis
    if redis-cli -h localhost -p 6379 ping > /dev/null 2>&1; then
        print_success "redis is healthy"
    else
        print_error "redis is not responding"
    fi
}

# Function to run complete demo
run_complete_demo() {
    print_demo "Running Complete Suricata ML-IDS Demo..."
    echo
    
    # Start services if not running
    if ! $COMPOSE_CMD ps | grep -q "Up"; then
        start_services
        echo
    fi
    
    # Wait for services to be ready
    print_demo "Waiting for services to be fully ready..."
    sleep 30
    
    # Run demo scenarios
    demo_feature_extraction
    echo
    
    demo_ml_training
    echo
    
    demo_realtime_detection
    echo
    
    print_demo "Demo completed! Access points:"
    echo "📊 Kibana Dashboards: http://localhost:5601"
    echo "🔍 Real-time Detector API: http://localhost:8080/docs"
    echo "🧠 ML Trainer API: http://localhost:8002/docs"
    echo "⚙️  Feature Extractor API: http://localhost:8001/docs"
    echo
    
    print_success "Complete demo finished successfully!"
}

# Function to clean up everything
cleanup() {
    print_status "Cleaning up Suricata ML-IDS..."
    
    # Stop services
    $COMPOSE_CMD down -v
    
    # Remove generated data (optional)
    read -p "Remove generated data? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf data/datasets/synthetic_network_traffic.csv
        rm -rf data/models/*
        rm -rf data/results/*
        rm -rf data/pcaps/samples/*
        print_success "Generated data removed"
    fi
    
    print_success "Cleanup completed!"
}

# Function to show help
show_help() {
    echo "Suricata ML-IDS Demo Script"
    echo
    echo "Usage: $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  start                 Start all services"
    echo "  stop                  Stop all services"
    echo "  restart               Restart all services"
    echo "  status                Show service status"
    echo "  logs [service]        Show logs (optionally for specific service)"
    echo "  demo                  Run complete demo (starts services if needed)"
    echo "  demo-ml               Run ML training demo only"
    echo "  demo-detection        Run real-time detection demo only"
    echo "  demo-extraction       Run feature extraction demo only"
    echo "  cleanup               Stop services and clean up data"
    echo "  help                  Show this help message"
    echo
    echo "Examples:"
    echo "  $0 start              # Start all services"
    echo "  $0 demo               # Run complete demonstration"
    echo "  $0 logs suricata      # Show Suricata logs"
    echo "  $0 status             # Check service health"
}

# Main script logic
main() {
    case "${1:-help}" in
        "start")
            start_services
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            restart_services
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs "${2:-}"
            ;;
        "demo")
            run_complete_demo
            ;;
        "demo-ml")
            demo_ml_training
            ;;
        "demo-detection")
            demo_realtime_detection
            ;;
        "demo-extraction")
            demo_feature_extraction
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run main function with all arguments
main "$@"
