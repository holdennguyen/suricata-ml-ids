# Feature Extractor API Documentation

## Overview

The Feature Extractor service processes PCAP files and extracts network features for machine learning analysis. It converts raw network traffic into structured feature vectors suitable for training and inference.

**Base URL**: `http://localhost:8001`  
**Service**: `feature-extractor`  
**Port**: `8001`

## Authentication

Currently, no authentication is required for API access.

## Endpoints

### Health Check

#### `GET /health`

Check the health status of the Feature Extractor service.

**Response**

```json
{
  "status": "healthy",
  "service": "feature-extractor"
}
```

**Status Codes**
- `200 OK` - Service is healthy
- `503 Service Unavailable` - Service is unhealthy

---

### Extract Features

#### `POST /extract`

Extract network features from a PCAP file and save them to a CSV file.

**Request Body**

```json
{
  "pcap_filename": "string",
  "output_filename": "string"
}
```

**Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `pcap_filename` | string | Yes | Name of the PCAP file to process (must exist in `/data/pcaps/` directory) |
| `output_filename` | string | No | Name of the output CSV file (defaults to `{pcap_filename}_features.csv`) |

**Example Request**

```bash
curl -X POST "http://localhost:8001/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "pcap_filename": "demo_traffic.pcap",
    "output_filename": "extracted_features.csv"
  }'
```

**Response**

```json
{
  "status": "success",
  "message": "Features extracted successfully",
  "input_file": "demo_traffic.pcap",
  "output_file": "extracted_features.csv",
  "features_extracted": 25,
  "packets_processed": 1500,
  "processing_time_ms": 245.7,
  "feature_summary": {
    "total_packets": 1500,
    "total_bytes": 150000,
    "unique_src_ips": 10,
    "unique_dst_ips": 15,
    "protocol_distribution": {
      "tcp": 0.75,
      "udp": 0.20,
      "icmp": 0.05
    }
  }
}
```

**Status Codes**
- `200 OK` - Features extracted successfully
- `400 Bad Request` - Invalid request parameters
- `404 Not Found` - PCAP file not found
- `500 Internal Server Error` - Processing error

**Error Response**

```json
{
  "status": "error",
  "message": "PCAP file not found: demo_traffic.pcap",
  "error_code": "FILE_NOT_FOUND"
}
```

---

### Batch Extract Features

#### `POST /batch-extract`

Extract features from multiple PCAP files in batch mode.

**Request Body**

```json
{
  "pcap_files": ["string"],
  "output_directory": "string"
}
```

**Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `pcap_files` | array[string] | Yes | List of PCAP filenames to process |
| `output_directory` | string | No | Directory for output CSV files (defaults to `/data/datasets/`) |

**Example Request**

```bash
curl -X POST "http://localhost:8001/batch-extract" \
  -H "Content-Type: application/json" \
  -d '{
    "pcap_files": ["traffic1.pcap", "traffic2.pcap"],
    "output_directory": "batch_results"
  }'
```

**Response**

```json
{
  "status": "success",
  "message": "Batch extraction completed",
  "files_processed": 2,
  "total_packets": 3000,
  "total_processing_time_ms": 567.3,
  "results": [
    {
      "input_file": "traffic1.pcap",
      "output_file": "traffic1_features.csv",
      "packets_processed": 1500,
      "processing_time_ms": 245.7
    },
    {
      "input_file": "traffic2.pcap", 
      "output_file": "traffic2_features.csv",
      "packets_processed": 1500,
      "processing_time_ms": 321.6
    }
  ]
}
```

## Feature Schema

The Feature Extractor generates 25+ network features from PCAP data:

### Basic Traffic Features
- `total_packets` - Total number of packets
- `total_bytes` - Total bytes transferred
- `avg_packet_size` - Average packet size in bytes
- `duration` - Flow duration in seconds
- `packets_per_second` - Packet rate

### Protocol Features
- `tcp_ratio` - Ratio of TCP packets (0.0-1.0)
- `udp_ratio` - Ratio of UDP packets (0.0-1.0)
- `icmp_ratio` - Ratio of ICMP packets (0.0-1.0)

### Connection Features
- `unique_src_ips` - Number of unique source IPs
- `unique_dst_ips` - Number of unique destination IPs
- `tcp_syn_ratio` - Ratio of TCP SYN packets
- `well_known_ports` - Ratio of well-known ports (0-1023)
- `high_ports` - Ratio of high ports (1024+)

### Content Features
- `payload_entropy` - Shannon entropy of payload data
- `fragmented_packets` - Ratio of fragmented packets
- `suspicious_flags` - Ratio of packets with suspicious TCP flags

### Application Features
- `http_requests` - Number of HTTP requests
- `dns_queries` - Number of DNS queries
- `tls_handshakes` - Number of TLS handshakes

### Security Features
- `port_scan_indicators` - Port scanning behavior indicators
- `ddos_indicators` - DDoS attack indicators
- `malware_indicators` - Malware communication indicators
- `data_exfiltration_indicators` - Data exfiltration indicators

## Error Handling

The API uses standard HTTP status codes and returns detailed error messages:

### Common Errors

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `FILE_NOT_FOUND` | 404 | PCAP file does not exist |
| `INVALID_FORMAT` | 400 | Invalid PCAP file format |
| `PROCESSING_ERROR` | 500 | Error during feature extraction |
| `INSUFFICIENT_DATA` | 400 | PCAP file contains insufficient data |

### Error Response Format

```json
{
  "status": "error",
  "message": "Human-readable error description",
  "error_code": "MACHINE_READABLE_CODE",
  "details": {
    "file": "problematic_file.pcap",
    "line": 42,
    "additional_info": "..."
  }
}
```

## Rate Limits

- **Extract Features**: 10 requests per minute
- **Batch Extract**: 5 requests per hour
- **Health Check**: No limit

## Performance

- **Average Processing Time**: ~200ms per 1000 packets
- **Memory Usage**: ~100MB per PCAP file
- **Supported File Sizes**: Up to 1GB PCAP files
- **Concurrent Requests**: Up to 5 simultaneous extractions

## Examples

### Python Client Example

```python
import requests
import json

# Extract features from a PCAP file
response = requests.post(
    "http://localhost:8001/extract",
    headers={"Content-Type": "application/json"},
    json={
        "pcap_filename": "demo_traffic.pcap",
        "output_filename": "demo_features.csv"
    }
)

if response.status_code == 200:
    result = response.json()
    print(f"Processed {result['packets_processed']} packets")
    print(f"Extracted {result['features_extracted']} features")
else:
    error = response.json()
    print(f"Error: {error['message']}")
```

### JavaScript Client Example

```javascript
const extractFeatures = async (pcapFile, outputFile) => {
  try {
    const response = await fetch('http://localhost:8001/extract', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        pcap_filename: pcapFile,
        output_filename: outputFile
      })
    });
    
    const result = await response.json();
    
    if (response.ok) {
      console.log(`Features extracted: ${result.features_extracted}`);
      return result;
    } else {
      throw new Error(result.message);
    }
  } catch (error) {
    console.error('Feature extraction failed:', error);
  }
};

// Usage
extractFeatures('demo_traffic.pcap', 'demo_features.csv');
```

## Integration Notes

- The Feature Extractor integrates with the ML Trainer service for model training
- Output CSV files are automatically saved to `/data/datasets/` directory
- Features are normalized and ready for machine learning algorithms
- The service supports both real-time and batch processing workflows
