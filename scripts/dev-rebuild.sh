#!/bin/bash

# Development rebuild script
# Ensures all code changes are applied to containers

set -e

SERVICE=${1:-"all"}
FORCE_CLEAN=${2:-"false"}

echo "🚀 Development rebuild for: $SERVICE"

# Function to rebuild a specific service
rebuild_service() {
    local service=$1
    echo "🔄 Rebuilding $service..."
    
    # Generate unique cache-bust value
    export CACHEBUST=$(date +%s%N)
    
    if [ "$FORCE_CLEAN" = "true" ]; then
        echo "🧹 Force cleaning Docker cache..."
        docker-compose down
        docker system prune -f
    fi
    
    # Build with no cache and cache-busting
    docker-compose build --no-cache --build-arg CACHEBUST=$CACHEBUST $service
    
    # Restart the service
    docker-compose up -d $service
    
    echo "✅ $service rebuilt successfully!"
}

# Function to test service health
test_service_health() {
    local service=$1
    local port=$2
    local endpoint=${3:-"health"}
    
    echo "🏥 Testing $service health..."
    sleep 3
    
    for i in {1..10}; do
        if curl -s "http://localhost:$port/$endpoint" > /dev/null 2>&1; then
            echo "✅ $service is healthy!"
            return 0
        fi
        echo "⏳ Waiting for $service... ($i/10)"
        sleep 2
    done
    
    echo "❌ $service health check failed"
    docker-compose logs --tail=10 $service
    return 1
}

# Main rebuild logic
case $SERVICE in
    "ml-trainer")
        rebuild_service "ml-trainer"
        test_service_health "ml-trainer" "8002"
        ;;
    "feature-extractor")
        rebuild_service "feature-extractor"
        test_service_health "feature-extractor" "8001"
        ;;
    "realtime-detector")
        rebuild_service "realtime-detector"
        test_service_health "realtime-detector" "8080"
        ;;
    "traffic-replay")
        rebuild_service "traffic-replay"
        test_service_health "traffic-replay" "8003"
        ;;
    "all")
        echo "🔄 Rebuilding all Python services..."
        export CACHEBUST=$(date +%s%N)
        
        if [ "$FORCE_CLEAN" = "true" ]; then
            echo "🧹 Force cleaning Docker cache..."
            docker-compose down
            docker system prune -f
        fi
        
        # Rebuild all Python services
        docker-compose build --no-cache --build-arg CACHEBUST=$CACHEBUST \
            ml-trainer feature-extractor realtime-detector traffic-replay
        
        # Start all services
        docker-compose up -d
        
        # Test all services
        echo "🏥 Testing all services..."
        sleep 5
        test_service_health "ml-trainer" "8002" || true
        test_service_health "feature-extractor" "8001" || true
        test_service_health "realtime-detector" "8080" || true
        test_service_health "traffic-replay" "8003" || true
        ;;
    *)
        echo "❌ Unknown service: $SERVICE"
        echo "Usage: $0 [ml-trainer|feature-extractor|realtime-detector|traffic-replay|all] [force-clean]"
        exit 1
        ;;
esac

echo "🎉 Development rebuild completed!"
echo ""
echo "📋 Available services:"
echo "   - ML Trainer: http://localhost:8002"
echo "   - Feature Extractor: http://localhost:8001"  
echo "   - Real-time Detector: http://localhost:8080"
echo "   - Traffic Replay: http://localhost:8003"
echo "   - OpenSearch: http://localhost:9201"
echo "   - OpenSearch Dashboards: http://localhost:5602"
