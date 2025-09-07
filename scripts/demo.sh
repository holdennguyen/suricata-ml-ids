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
        local total_services=9
        
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
        
        # Check traffic-replay
        if curl -f -s http://localhost:8003/health > /dev/null 2>&1; then
            ((healthy_services++))
        fi
        
        # Check Elasticsearch
        if curl -f -s http://localhost:9200/_cluster/health > /dev/null 2>&1; then
            ((healthy_services++))
        fi
        
        # Check Kibana
        if curl -f -s http://localhost:5601/api/status > /dev/null 2>&1; then
            ((healthy_services++))
        fi
        
        # Check Redis
        if docker exec redis redis-cli ping > /dev/null 2>&1; then
            ((healthy_services++))
        fi
        
        # Check Suricata
        if docker exec suricata-ids ps aux | grep -v grep | grep suricata > /dev/null 2>&1; then
            ((healthy_services++))
        fi
        
        # Check Log Shipper
        if docker logs log-shipper --tail 1 2>&1 | grep -q "Successfully indexed\|Streamed.*events"; then
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
    $COMPOSE_CMD up -d kibana suricata log-shipper feature-extractor ml-trainer realtime-detector traffic-replay
    
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
    print_demo "Running ML Training Demo with NSL-KDD Dataset..."
    
    # Train models using NSL-KDD sample dataset (will auto-download if not exists)
    print_demo "Training Decision Tree, k-NN, and Ensemble models on NSL-KDD data..."
    
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
         }' | jq '.'
    
    print_success "ML training demo with NSL-KDD completed!"
}

# Function to run real-time detection demo
demo_realtime_detection() {
    print_demo "Running Comprehensive Real-time Detection Demo..."
    print_demo "Testing all NSL-KDD attack categories: DoS, Probe, R2L, U2R + Normal traffic"
    
    # 1. Normal Traffic Simulation
    print_demo "🟢 Testing Normal Network Traffic (Web browsing)..."
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
             "suspicious_flags": 0.05,
             "http_requests": 10,
             "dns_queries": 5,
             "tls_handshakes": 3
           },
           "source_ip": "192.168.1.100",
           "dest_ip": "10.0.0.50"
         }' | jq '{prediction: .prediction, confidence: .confidence, threat_score: .threat_score, processing_time_ms: .processing_time_ms}'
    
    # 2. DoS Attack Simulation (Denial of Service)
    print_demo "🔴 Testing DoS Attack (SYN Flood pattern)..."
    curl -X POST "http://localhost:8080/detect" \
         -H "Content-Type: application/json" \
         -d '{
           "features": {
             "total_packets": 1000,
             "total_bytes": 50000,
             "avg_packet_size": 50.0,
             "duration": 1.0,
             "tcp_ratio": 0.98,
             "udp_ratio": 0.02,
             "icmp_ratio": 0.0,
             "packets_per_second": 1000.0,
             "unique_src_ips": 1,
             "unique_dst_ips": 100,
             "tcp_syn_ratio": 0.95,
             "well_known_ports": 0.1,
             "high_ports": 0.9,
             "payload_entropy": 2.5,
             "suspicious_flags": 0.9,
             "http_requests": 0,
             "dns_queries": 0,
             "tls_handshakes": 0
           },
           "source_ip": "10.0.0.100",
           "dest_ip": "192.168.1.0/24"
         }' | jq '{prediction: .prediction, confidence: .confidence, threat_score: .threat_score, processing_time_ms: .processing_time_ms}'
    
    # 3. Probe Attack Simulation (Port Scanning)
    print_demo "🟡 Testing Probe Attack (Port Scan pattern)..."
    curl -X POST "http://localhost:8080/detect" \
         -H "Content-Type: application/json" \
         -d '{
           "features": {
             "total_packets": 200,
             "total_bytes": 12800,
             "avg_packet_size": 64.0,
             "duration": 2.0,
             "tcp_ratio": 1.0,
             "udp_ratio": 0.0,
             "icmp_ratio": 0.0,
             "packets_per_second": 100.0,
             "unique_src_ips": 1,
             "unique_dst_ips": 50,
             "tcp_syn_ratio": 1.0,
             "well_known_ports": 0.8,
             "high_ports": 0.2,
             "payload_entropy": 1.5,
             "suspicious_flags": 0.7,
             "http_requests": 0,
             "dns_queries": 0,
             "tls_handshakes": 0
           },
           "source_ip": "10.0.0.101",
           "dest_ip": "192.168.1.50"
         }' | jq '{prediction: .prediction, confidence: .confidence, threat_score: .threat_score, processing_time_ms: .processing_time_ms}'
    
    # 4. R2L Attack Simulation (Remote to Local - Password Guessing)
    print_demo "🟠 Testing R2L Attack (Password Guessing pattern)..."
    curl -X POST "http://localhost:8080/detect" \
         -H "Content-Type: application/json" \
         -d '{
           "features": {
             "total_packets": 50,
             "total_bytes": 6400,
             "avg_packet_size": 128.0,
             "duration": 10.0,
             "tcp_ratio": 1.0,
             "udp_ratio": 0.0,
             "icmp_ratio": 0.0,
             "packets_per_second": 5.0,
             "unique_src_ips": 1,
             "unique_dst_ips": 1,
             "tcp_syn_ratio": 0.2,
             "well_known_ports": 1.0,
             "high_ports": 0.0,
             "payload_entropy": 6.5,
             "suspicious_flags": 0.1,
             "http_requests": 0,
             "dns_queries": 0,
             "tls_handshakes": 0
           },
           "source_ip": "203.0.113.100",
           "dest_ip": "192.168.1.50"
         }' | jq '{prediction: .prediction, confidence: .confidence, threat_score: .threat_score, processing_time_ms: .processing_time_ms}'
    
    # 5. U2R Attack Simulation (User to Root - Buffer Overflow)
    print_demo "🔵 Testing U2R Attack (Buffer Overflow pattern)..."
    curl -X POST "http://localhost:8080/detect" \
         -H "Content-Type: application/json" \
         -d '{
           "features": {
             "total_packets": 10,
             "total_bytes": 8192,
             "avg_packet_size": 819.2,
             "duration": 1.0,
             "tcp_ratio": 1.0,
             "udp_ratio": 0.0,
             "icmp_ratio": 0.0,
             "packets_per_second": 10.0,
             "unique_src_ips": 1,
             "unique_dst_ips": 1,
             "tcp_syn_ratio": 0.1,
             "well_known_ports": 1.0,
             "high_ports": 0.0,
             "payload_entropy": 7.8,
             "suspicious_flags": 0.2,
             "http_requests": 0,
             "dns_queries": 0,
             "tls_handshakes": 0
           },
           "source_ip": "192.168.1.100",
           "dest_ip": "192.168.1.10"
         }' | jq '{prediction: .prediction, confidence: .confidence, threat_score: .threat_score, processing_time_ms: .processing_time_ms}'
    
    # 6. Batch Detection with Mixed Traffic
    print_demo "📊 Testing Batch Detection with Mixed Attack Types..."
    curl -X POST "http://localhost:8080/batch-detect" \
         -H "Content-Type: application/json" \
         -d '[
           {
             "features": {
               "total_packets": 80,
               "total_bytes": 8000,
               "avg_packet_size": 100.0,
               "duration": 3.0,
               "tcp_ratio": 0.9,
               "udp_ratio": 0.1,
               "icmp_ratio": 0.0,
               "packets_per_second": 26.7,
               "unique_src_ips": 1,
               "unique_dst_ips": 2,
               "tcp_syn_ratio": 0.5,
               "well_known_ports": 0.7,
               "high_ports": 0.3,
               "payload_entropy": 7.2,
               "suspicious_flags": 0.02,
               "http_requests": 5,
               "dns_queries": 2,
               "tls_handshakes": 1
             },
             "source_ip": "192.168.1.200"
           },
           {
             "features": {
               "total_packets": 500,
               "total_bytes": 25000,
               "avg_packet_size": 50.0,
               "duration": 0.5,
               "tcp_ratio": 1.0,
               "udp_ratio": 0.0,
               "icmp_ratio": 0.0,
               "packets_per_second": 1000.0,
               "unique_src_ips": 1,
               "unique_dst_ips": 50,
               "tcp_syn_ratio": 0.98,
               "well_known_ports": 0.2,
               "high_ports": 0.8,
               "payload_entropy": 2.0,
               "suspicious_flags": 0.95,
               "http_requests": 0,
               "dns_queries": 0,
               "tls_handshakes": 0
             },
             "source_ip": "10.0.0.200"
           }
         ]' | jq '{batch_size: .batch_size, avg_processing_time_ms: .avg_processing_time_ms, results: .results | map({prediction: .prediction, confidence: .confidence, threat_score: .threat_score})}'
    
    # 7. Traffic Simulation
    print_demo "🌐 Generating Realistic Mixed Traffic Simulation..."
    curl -X POST "http://localhost:8003/replay" \
         -H "Content-Type: application/json" \
         -d '{
           "scenario": "comprehensive_attack_demo",
           "duration_seconds": 30,
           "packets_per_second": 100,
           "attack_ratio": 0.3,
           "protocols": ["tcp", "udp"],
           "attack_types": ["dos", "probe"]
         }' 2>/dev/null | jq '.' || print_warning "Traffic replay service not available"
    
    print_demo "⏳ Waiting for traffic simulation (30 seconds)..."
    sleep 5  # Reduced wait time for demo
    
    # 8. Create Sample Alerts in Elasticsearch
    print_demo "📝 Creating Sample Suricata Alerts for each attack type..."
    
    # DoS Alert
    curl -X POST "http://localhost:9200/suricata-alerts-$(date +%Y.%m)/_doc" \
         -H "Content-Type: application/json" \
         -d "{
           \"@timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%S.000Z)\",
           \"event_type\": \"alert\",
           \"alert\": {
             \"signature\": \"DoS SYN Flood Attack Detected\",
             \"category\": \"Denial of Service\",
             \"severity\": 1,
             \"attack_type\": \"dos\"
           },
           \"src_ip\": \"10.0.0.100\",
           \"dest_ip\": \"192.168.1.10\",
           \"src_port\": 12345,
           \"dest_port\": 80,
           \"proto\": \"TCP\"
         }" > /dev/null
    
    # Probe Alert
    curl -X POST "http://localhost:9200/suricata-alerts-$(date +%Y.%m)/_doc" \
         -H "Content-Type: application/json" \
         -d "{
           \"@timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%S.000Z)\",
           \"event_type\": \"alert\",
           \"alert\": {
             \"signature\": \"Port Scan Detected\",
             \"category\": \"Attempted Reconnaissance\",
             \"severity\": 2,
             \"attack_type\": \"probe\"
           },
           \"src_ip\": \"10.0.0.101\",
           \"dest_ip\": \"192.168.1.50\",
           \"src_port\": 54321,
           \"dest_port\": 22,
           \"proto\": \"TCP\"
         }" > /dev/null
    
    # R2L Alert
    curl -X POST "http://localhost:9200/suricata-alerts-$(date +%Y.%m)/_doc" \
         -H "Content-Type: application/json" \
         -d "{
           \"@timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%S.000Z)\",
           \"event_type\": \"alert\",
           \"alert\": {
             \"signature\": \"Brute Force Login Attempt\",
             \"category\": \"Authentication Failure\",
             \"severity\": 2,
             \"attack_type\": \"r2l\"
           },
           \"src_ip\": \"203.0.113.100\",
           \"dest_ip\": \"192.168.1.50\",
           \"src_port\": 45678,
           \"dest_port\": 22,
           \"proto\": \"TCP\"
         }" > /dev/null
    
    # U2R Alert
    curl -X POST "http://localhost:9200/suricata-alerts-$(date +%Y.%m)/_doc" \
         -H "Content-Type: application/json" \
         -d "{
           \"@timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%S.000Z)\",
           \"event_type\": \"alert\",
           \"alert\": {
             \"signature\": \"Buffer Overflow Attempt Detected\",
             \"category\": \"Attempted Administrator Privilege Gain\",
             \"severity\": 1,
             \"attack_type\": \"u2r\"
           },
           \"src_ip\": \"192.168.1.100\",
           \"dest_ip\": \"192.168.1.10\",
           \"src_port\": 33445,
           \"dest_port\": 21,
           \"proto\": \"TCP\"
         }" > /dev/null
    
    # Create ML Detection Results
    print_demo "🤖 Creating Sample ML Detection Results..."
    curl -X POST "http://localhost:9200/ml-detections-$(date +%Y.%m)/_doc" \
         -H "Content-Type: application/json" \
         -d "{
           \"@timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%S.000Z)\",
           \"prediction\": \"attack\",
           \"confidence\": 0.95,
           \"threat_score\": 9.2,
           \"model_used\": \"ensemble\",
           \"attack_type\": \"dos\",
           \"processing_time_ms\": 12,
           \"src_ip\": \"10.0.0.100\",
           \"dest_ip\": \"192.168.1.10\"
         }" > /dev/null
    
    print_success "✅ Comprehensive attack simulation completed!"
    print_success "📊 Demo Results Summary:"
    print_success "   • Normal Traffic: Expected low threat scores"
    print_success "   • DoS Attack: High confidence attack detection"
    print_success "   • Probe Attack: Port scan pattern recognition"
    print_success "   • R2L Attack: Authentication-based intrusion"
    print_success "   • U2R Attack: Privilege escalation detection"
    print_success ""
    print_success "🌐 View results in Kibana: http://localhost:5601"
    print_success "   • Suricata alerts for all attack types"
    print_success "   • ML detection results with confidence scores"
    print_success "   • Real-time traffic analysis and patterns"
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
        "traffic-replay:8003:/health"
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
    if docker exec redis redis-cli ping > /dev/null 2>&1; then
        print_success "redis is healthy"
    else
        print_error "redis is not responding"
    fi
    
    # Check Suricata
    if docker exec suricata-ids ps aux | grep -v grep | grep suricata > /dev/null 2>&1; then
        print_success "suricata is healthy"
    else
        print_error "suricata is not responding"
    fi
    
    # Check Log Shipper
    if docker logs log-shipper --tail 1 2>&1 | grep -q "Successfully indexed\|Streamed.*events"; then
        print_success "log-shipper is healthy"
    else
        print_error "log-shipper is not responding"
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
        # Synthetic data files removed (now using NSL-KDD)
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
