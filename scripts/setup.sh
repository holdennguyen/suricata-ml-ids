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
    mkdir -p data/{pcaps,datasets,models,results,logs}
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

# Setup NSL-KDD dataset
setup_nsl_kdd_dataset() {
    print_status "Setting up NSL-KDD dataset for ML training..."
    
    # Run NSL-KDD dataset preparation if script exists
    if [ -f "data/download_nsl_kdd.py" ]; then
        cd data && python3 download_nsl_kdd.py
        cd ..
        print_success "NSL-KDD dataset prepared successfully!"
    else
        print_warning "NSL-KDD download script not found. Dataset will be downloaded automatically during first ML training."
    fi
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
    setup_nsl_kdd_dataset
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
