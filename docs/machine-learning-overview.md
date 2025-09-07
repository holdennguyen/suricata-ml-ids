# Machine Learning Overview

## 🎯 Quick Summary

The Suricata ML-IDS uses **three machine learning algorithms** trained on the **NSL-KDD dataset** to detect network intrusions with **99.2% accuracy** in real-time.

## 📊 Dataset: NSL-KDD

- **148,517 samples** of real network traffic
- **122 features** after preprocessing  
- **Binary classification**: Normal vs Attack traffic
- **Industry benchmark** for intrusion detection research

## 🧠 Machine Learning Models

### 1. Decision Tree (98.8% accuracy)
- Creates yes/no decision rules
- Fast and interpretable
- Good for understanding attack patterns

### 2. k-Nearest Neighbors (98.9% accuracy)  
- Classifies based on similar past examples
- Excellent for detecting subtle variations
- Memory-based learning approach

### 3. Ensemble Model (99.2% accuracy)
- Combines Decision Tree + k-NN predictions
- Best overall performance
- Reduces individual model errors

## ⚡ Real-time Performance

- **Detection Speed**: 8-29ms per request
- **Throughput**: 1000+ requests/second
- **Memory Usage**: <2GB total
- **Latency Target**: <100ms (achieved: <30ms)

## 🔄 Training Process

```bash
# Train models with NSL-KDD data
./scripts/demo.sh demo-ml

# Expected results:
# - Decision Tree: 98.8% accuracy in 1.4s
# - k-NN: 98.9% accuracy in 2.1s  
# - Ensemble: 99.2% accuracy in 5.3s
```

## 🎯 Detection API

```bash
# Test real-time detection
curl -X POST "http://localhost:8080/detect" \
     -H "Content-Type: application/json" \
     -d '{
       "features": {
         "duration": 0.001,
         "src_bytes": 60,
         "count": 100,
         "serror_rate": 0.8
       }
     }'

# Response:
{
  "prediction": "attack",
  "confidence": 0.992,
  "threat_score": 0.85,
  "processing_time_ms": 15.2
}
```

## 📈 Key Features for Attack Detection

1. **serror_rate**: Connection error patterns
2. **count**: Rapid connection attempts  
3. **dst_host_srv_count**: Service targeting patterns
4. **srv_count**: Service diversity
5. **duration**: Connection timing anomalies

## 🔍 Attack Types Detected

- **DoS**: Denial of Service attacks
- **Probe**: Port scans and reconnaissance  
- **R2L**: Remote to Local access attempts
- **U2R**: User to Root privilege escalation

## 📚 For More Details

- **Beginners**: See [ML Guide for Beginners](ml-guide-for-beginners.md)
- **API Reference**: See [API Documentation](api/)
- **Performance**: See main README performance section
