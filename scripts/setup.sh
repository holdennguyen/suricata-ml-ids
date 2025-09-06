#!/bin/bash

# Setup script for Suricata ML-IDS
# Prepares the environment and downloads necessary data

set -e

echo "🚀 Setting up Suricata ML-IDS..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Check if Docker is installed and running
check_docker() {
    print_status "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running. Please start Docker."
        exit 1
    fi
    
    print_success "Docker is installed and running"
}

# Check if Docker Compose is available
check_docker_compose() {
    print_status "Checking Docker Compose..."
    
    if docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
    elif command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        print_error "Docker Compose is not available. Please install Docker Compose."
        exit 1
    fi
    
    print_success "Docker Compose is available: $COMPOSE_CMD"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    # Data directories
    mkdir -p data/{pcaps,datasets,models,results,logs,synthetic}
    mkdir -p data/opensearch
    
    # Ensure proper permissions
    chmod -R 755 data/
    
    print_success "Directories created successfully"
}

# Download sample PCAP files for testing
download_sample_data() {
    print_status "Downloading sample network traffic data..."
    
    # Create sample PCAP directory if it doesn't exist
    mkdir -p data/pcaps/samples
    
    # Download sample PCAP files (using curl with fallback URLs)
    PCAP_URLS=(
        "https://www.malware-traffic-analysis.net/2023/01/03/2023-01-03-traffic-analysis-exercise.pcap"
        "https://download.netresec.com/pcap/maccdc-2012/maccdc2012_00000.pcap"
    )
    
    for url in "${PCAP_URLS[@]}"; do
        filename=$(basename "$url")
        if [ ! -f "data/pcaps/samples/$filename" ]; then
            print_status "Downloading $filename..."
            if curl -L -f -o "data/pcaps/samples/$filename" "$url" 2>/dev/null; then
                print_success "Downloaded $filename"
            else
                print_warning "Failed to download $filename (network issue or URL changed)"
            fi
        else
            print_status "$filename already exists, skipping..."
        fi
    done
}

# Generate synthetic training data
generate_synthetic_data() {
    print_status "Generating synthetic training data..."
    
    # Create a Python script to generate synthetic network features
    cat > data/generate_synthetic_data.py << 'EOF'
#!/usr/bin/env python3
"""
Generate synthetic network traffic features for ML training
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Set random seed for reproducibility
np.random.seed(42)

def generate_normal_traffic(n_samples=1000):
    """Generate normal network traffic features"""
    data = []
    
    for _ in range(n_samples):
        # Normal traffic characteristics
        features = {
            'total_packets': np.random.normal(50, 15),
            'total_bytes': np.random.normal(5000, 1500),
            'avg_packet_size': np.random.normal(100, 30),
            'duration': np.random.exponential(10),
            'tcp_ratio': np.random.beta(8, 2),  # High TCP ratio for normal traffic
            'udp_ratio': np.random.beta(2, 8),  # Low UDP ratio
            'icmp_ratio': np.random.beta(1, 20), # Very low ICMP
            'packets_per_second': np.random.gamma(2, 5),
            'unique_src_ips': np.random.poisson(2) + 1,
            'unique_dst_ips': np.random.poisson(3) + 1,
            'tcp_syn_ratio': np.random.beta(2, 8),
            'well_known_ports': np.random.poisson(5),
            'high_ports': np.random.poisson(10),
            'payload_entropy': np.random.normal(6, 1),
            'fragmented_packets': np.random.poisson(0.1),
            'suspicious_flags': 0,
            'http_requests': np.random.poisson(5),
            'dns_queries': np.random.poisson(3),
            'tls_handshakes': np.random.poisson(2),
            'label': 'normal'
        }
        
        # Ensure positive values
        for key, value in features.items():
            if key != 'label' and value < 0:
                features[key] = 0
                
        data.append(features)
    
    return data

def generate_attack_traffic(n_samples=200):
    """Generate attack traffic features"""
    data = []
    
    attack_types = ['port_scan', 'dos', 'brute_force', 'malware']
    
    for _ in range(n_samples):
        attack_type = np.random.choice(attack_types)
        
        if attack_type == 'port_scan':
            features = {
                'total_packets': np.random.normal(200, 50),
                'total_bytes': np.random.normal(20000, 5000),
                'avg_packet_size': np.random.normal(60, 10),  # Smaller packets
                'duration': np.random.exponential(30),
                'tcp_ratio': np.random.beta(9, 1),  # Very high TCP
                'udp_ratio': np.random.beta(1, 9),
                'icmp_ratio': np.random.beta(1, 20),
                'packets_per_second': np.random.gamma(5, 10),  # High rate
                'unique_src_ips': 1,  # Single source
                'unique_dst_ips': np.random.poisson(50) + 10,  # Many destinations
                'tcp_syn_ratio': np.random.beta(9, 1),  # High SYN ratio
                'well_known_ports': np.random.poisson(20),  # Scanning many ports
                'high_ports': np.random.poisson(30),
                'payload_entropy': np.random.normal(3, 0.5),  # Low entropy
                'fragmented_packets': np.random.poisson(0.5),
                'suspicious_flags': np.random.poisson(5),
                'http_requests': 0,
                'dns_queries': 0,
                'tls_handshakes': 0,
                'label': 'attack'
            }
        
        elif attack_type == 'dos':
            features = {
                'total_packets': np.random.normal(1000, 200),  # High volume
                'total_bytes': np.random.normal(100000, 20000),
                'avg_packet_size': np.random.normal(100, 20),
                'duration': np.random.exponential(5),  # Short duration
                'tcp_ratio': np.random.beta(8, 2),
                'udp_ratio': np.random.beta(2, 8),
                'icmp_ratio': np.random.beta(1, 10),
                'packets_per_second': np.random.gamma(10, 20),  # Very high rate
                'unique_src_ips': np.random.poisson(3) + 1,
                'unique_dst_ips': 1,  # Single target
                'tcp_syn_ratio': np.random.beta(9, 1),  # SYN flood
                'well_known_ports': np.random.poisson(2),
                'high_ports': np.random.poisson(5),
                'payload_entropy': np.random.normal(2, 0.5),  # Very low entropy
                'fragmented_packets': np.random.poisson(2),
                'suspicious_flags': np.random.poisson(10),
                'http_requests': 0,
                'dns_queries': 0,
                'tls_handshakes': 0,
                'label': 'attack'
            }
        
        elif attack_type == 'brute_force':
            features = {
                'total_packets': np.random.normal(300, 50),
                'total_bytes': np.random.normal(30000, 5000),
                'avg_packet_size': np.random.normal(120, 20),
                'duration': np.random.exponential(60),  # Longer duration
                'tcp_ratio': np.random.beta(9, 1),  # High TCP
                'udp_ratio': np.random.beta(1, 9),
                'icmp_ratio': 0,
                'packets_per_second': np.random.gamma(3, 5),  # Moderate rate
                'unique_src_ips': 1,
                'unique_dst_ips': 1,
                'tcp_syn_ratio': np.random.beta(6, 4),
                'well_known_ports': np.random.poisson(1) + 1,  # Targeting specific service
                'high_ports': np.random.poisson(2),
                'payload_entropy': np.random.normal(5, 1),
                'fragmented_packets': 0,
                'suspicious_flags': np.random.poisson(2),
                'http_requests': np.random.poisson(50),  # Many failed attempts
                'dns_queries': 0,
                'tls_handshakes': np.random.poisson(50),
                'label': 'attack'
            }
        
        else:  # malware
            features = {
                'total_packets': np.random.normal(150, 30),
                'total_bytes': np.random.normal(15000, 3000),
                'avg_packet_size': np.random.normal(200, 50),  # Larger packets
                'duration': np.random.exponential(20),
                'tcp_ratio': np.random.beta(7, 3),
                'udp_ratio': np.random.beta(3, 7),
                'icmp_ratio': np.random.beta(2, 18),
                'packets_per_second': np.random.gamma(4, 8),
                'unique_src_ips': 1,
                'unique_dst_ips': np.random.poisson(5) + 1,  # Command & control
                'tcp_syn_ratio': np.random.beta(5, 5),
                'well_known_ports': np.random.poisson(3),
                'high_ports': np.random.poisson(15),  # Using high ports
                'payload_entropy': np.random.normal(7, 0.5),  # High entropy (encrypted)
                'fragmented_packets': np.random.poisson(1),
                'suspicious_flags': np.random.poisson(3),
                'http_requests': np.random.poisson(10),
                'dns_queries': np.random.poisson(20),  # DNS tunneling
                'tls_handshakes': np.random.poisson(8),
                'label': 'attack'
            }
        
        # Ensure positive values
        for key, value in features.items():
            if key != 'label' and value < 0:
                features[key] = 0
                
        data.append(features)
    
    return data

def main():
    print("Generating synthetic network traffic data...")
    
    # Generate normal and attack traffic
    normal_data = generate_normal_traffic(2000)
    attack_data = generate_attack_traffic(500)
    
    # Combine data
    all_data = normal_data + attack_data
    
    # Create DataFrame
    df = pd.DataFrame(all_data)
    
    # Shuffle the data
    df = df.sample(frac=1).reset_index(drop=True)
    
    # Save to CSV
    output_path = Path('datasets/synthetic_network_traffic.csv')
    output_path.parent.mkdir(exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print(f"Generated {len(df)} samples:")
    print(f"- Normal traffic: {len(normal_data)} samples")
    print(f"- Attack traffic: {len(attack_data)} samples")
    print(f"- Saved to: {output_path}")
    
    # Print basic statistics
    print("\nDataset statistics:")
    print(df.describe())
    
    print("\nLabel distribution:")
    print(df['label'].value_counts())

if __name__ == "__main__":
    main()
EOF

    # Run the synthetic data generation
    cd data && python3 generate_synthetic_data.py
    cd ..
    
    print_success "Synthetic training data generated"
}

# Pull required Docker images
pull_docker_images() {
    print_status "Pulling required Docker images..."
    
    # Pull base images to speed up builds
    docker pull python:3.9-slim
    docker pull suricata/suricata:7.0.2
    docker pull opensearchproject/opensearch:2.11.0
    docker pull opensearchproject/opensearch-dashboards:2.11.0
    docker pull redis:7-alpine
    
    print_success "Docker images pulled successfully"
}

# Build all services
build_services() {
    print_status "Building all services..."
    
    # Build all services using docker-compose
    $COMPOSE_CMD build --parallel
    
    print_success "All services built successfully"
}

# Initialize OpenSearch
init_opensearch() {
    print_status "Preparing OpenSearch configuration..."
    
    # Create OpenSearch configuration
    mkdir -p services/opensearch/config
    
    # Create opensearch.yml
    cat > services/opensearch/config/opensearch.yml << 'EOF'
cluster.name: ids-cluster
node.name: opensearch-node1
network.host: 0.0.0.0
http.port: 9200
discovery.seed_hosts: ["opensearch-node1"]
cluster.initial_cluster_manager_nodes: ["opensearch-node1"]
bootstrap.memory_lock: true

# Security settings (disabled for demo)
plugins.security.disabled: true

# Performance settings
indices.query.bool.max_clause_count: 10000
search.max_buckets: 100000
EOF
    
    # Create dashboards configuration
    mkdir -p services/opensearch/dashboards
    cat > services/opensearch/dashboards/opensearch_dashboards.yml << 'EOF'
server.name: opensearch-dashboards
server.host: "0.0.0.0"
opensearch.hosts: ["http://opensearch:9200"]

# Security settings (disabled for demo)
opensearch_security.multitenancy.enabled: false
opensearch_security.readonly_mode.roles: []
EOF
    
    print_success "OpenSearch configuration prepared"
}

# Create environment file
create_env_file() {
    print_status "Creating environment configuration..."
    
    cat > .env << 'EOF'
# Suricata ML-IDS Environment Configuration

# Service Configuration
COMPOSE_PROJECT_NAME=suricata-ml-ids

# ML Configuration
ML_ACCURACY_TARGET=0.90
LATENCY_TARGET_MS=100

# Redis Configuration
REDIS_URL=redis://redis:6379

# OpenSearch Configuration
OPENSEARCH_JAVA_OPTS=-Xms2g -Xmx2g
DISABLE_SECURITY_PLUGIN=true

# Logging
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1

# Data Paths
PCAP_PATH=./data/pcaps
DATASETS_PATH=./data/datasets
MODELS_PATH=./data/models
RESULTS_PATH=./data/results
LOGS_PATH=./data/logs
EOF
    
    print_success "Environment file created"
}

# Main setup function
main() {
    echo "========================================="
    echo "🛡️  Suricata ML-IDS Setup"
    echo "========================================="
    echo
    
    check_docker
    check_docker_compose
    create_directories
    download_sample_data
    generate_synthetic_data
    pull_docker_images
    init_opensearch
    create_env_file
    build_services
    
    echo
    echo "========================================="
    print_success "Setup completed successfully!"
    echo "========================================="
    echo
    echo "Next steps:"
    echo "1. Start the system: ./scripts/demo.sh start"
    echo "2. Run demo scenarios: ./scripts/demo.sh demo"
    echo "3. Access dashboards: http://localhost:5601"
    echo "4. API documentation: http://localhost:8080/docs"
    echo
    echo "For more information, see the documentation in docs/"
}

# Run main function
main "$@"
