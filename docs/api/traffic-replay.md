# Traffic Replay API Documentation

## Overview

The Traffic Replay service simulates network traffic patterns for testing and demonstration purposes. It can replay PCAP files, generate synthetic traffic, and create realistic network scenarios for IDS testing.

**Base URL**: `http://localhost:8003`  
**Service**: `traffic-replay`  
**Port**: `8003`

## Authentication

Currently, no authentication is required for API access.

## Endpoints

### Health Check

#### `GET /health`

Check the health status of the Traffic Replay service.

**Response**

```json
{
  "status": "healthy",
  "service": "traffic-replay"
}
```

**Status Codes**
- `200 OK` - Service is healthy
- `503 Service Unavailable` - Service is unhealthy

---

### Replay Traffic

#### `POST /replay`

Replay network traffic from a PCAP file with configurable parameters.

**Request Body**

```json
{
  "pcap_file": "demo_traffic.pcap",
  "replay_speed": 1.0,
  "loop_count": 1,
  "target_interface": "eth0",
  "packet_filter": "tcp or udp",
  "delay_between_packets": 0.0,
  "randomize_timing": false
}
```

**Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `pcap_file` | string | Yes | Name of PCAP file in `/data/pcaps/` directory |
| `replay_speed` | float | No | Speed multiplier (0.1-10.0, default: 1.0) |
| `loop_count` | integer | No | Number of replay loops (1-100, default: 1) |
| `target_interface` | string | No | Network interface for replay (default: "eth0") |
| `packet_filter` | string | No | BPF filter for packet selection |
| `delay_between_packets` | float | No | Additional delay in seconds (default: 0.0) |
| `randomize_timing` | boolean | No | Randomize packet timing (default: false) |

**Example Request**

```bash
curl -X POST "http://localhost:8003/replay" \
  -H "Content-Type: application/json" \
  -d '{
    "pcap_file": "demo_traffic.pcap",
    "replay_speed": 2.0,
    "loop_count": 3,
    "packet_filter": "tcp port 80 or tcp port 443"
  }'
```

**Response**

```json
{
  "status": "success",
  "message": "Traffic replay completed",
  "replay_id": "replay_20240115_103045",
  "statistics": {
    "packets_sent": 4500,
    "bytes_sent": 450000,
    "duration_seconds": 45.5,
    "packets_per_second": 98.9,
    "replay_speed": 2.0,
    "loops_completed": 3
  },
  "traffic_summary": {
    "tcp_packets": 3375,
    "udp_packets": 900,
    "icmp_packets": 225,
    "unique_flows": 135,
    "protocols": {
      "http": 1200,
      "https": 1800,
      "dns": 300,
      "other": 1200
    }
  },
  "processing_time_ms": 45500,
  "start_time": "2024-01-15T10:30:45Z",
  "end_time": "2024-01-15T10:31:30Z"
}
```

**Status Codes**
- `200 OK` - Replay completed successfully
- `400 Bad Request` - Invalid parameters
- `404 Not Found` - PCAP file not found
- `500 Internal Server Error` - Replay error

---

### Generate Synthetic Traffic

#### `POST /generate`

Generate synthetic network traffic with configurable attack patterns.

**Request Body**

```json
{
  "traffic_type": "mixed",
  "duration_seconds": 60,
  "packets_per_second": 100,
  "attack_ratio": 0.3,
  "output_file": "synthetic_traffic.pcap",
  "attack_types": ["port_scan", "ddos", "malware"],
  "protocols": ["tcp", "udp", "icmp"],
  "ip_ranges": {
    "src": "192.168.1.0/24",
    "dst": "10.0.0.0/16"
  }
}
```

**Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `traffic_type` | string | No | "normal", "attack", "mixed" (default: "mixed") |
| `duration_seconds` | integer | No | Generation duration (1-3600, default: 60) |
| `packets_per_second` | integer | No | Packet rate (1-10000, default: 100) |
| `attack_ratio` | float | No | Ratio of attack traffic (0.0-1.0, default: 0.3) |
| `output_file` | string | No | Output PCAP filename |
| `attack_types` | array | No | Types of attacks to simulate |
| `protocols` | array | No | Network protocols to include |
| `ip_ranges` | object | No | Source and destination IP ranges |

**Example Request**

```bash
curl -X POST "http://localhost:8003/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "traffic_type": "mixed",
    "duration_seconds": 120,
    "packets_per_second": 200,
    "attack_ratio": 0.4,
    "output_file": "test_traffic.pcap",
    "attack_types": ["port_scan", "ddos"],
    "protocols": ["tcp", "udp"]
  }'
```

**Response**

```json
{
  "status": "success",
  "message": "Synthetic traffic generated",
  "output_file": "test_traffic.pcap",
  "generation_id": "gen_20240115_103045",
  "statistics": {
    "total_packets": 24000,
    "normal_packets": 14400,
    "attack_packets": 9600,
    "file_size_mb": 9.6,
    "generation_time_ms": 2450.7
  },
  "traffic_breakdown": {
    "protocols": {
      "tcp": 18000,
      "udp": 6000
    },
    "attack_types": {
      "port_scan": 4800,
      "ddos": 4800
    },
    "flows": {
      "normal_flows": 240,
      "attack_flows": 160
    }
  },
  "file_info": {
    "path": "/data/pcaps/test_traffic.pcap",
    "size_bytes": 10066329,
    "created_at": "2024-01-15T10:30:45Z"
  }
}
```

---

### List Available PCAP Files

#### `GET /pcaps`

List all available PCAP files for replay.

**Response**

```json
{
  "pcap_files": [
    {
      "filename": "demo_traffic.pcap",
      "size_mb": 2.4,
      "packets": 1500,
      "duration_seconds": 30.5,
      "created_at": "2024-01-15T09:00:00Z",
      "protocols": ["tcp", "udp", "icmp"]
    },
    {
      "filename": "attack_samples.pcap",
      "size_mb": 5.7,
      "packets": 3200,
      "duration_seconds": 65.2,
      "created_at": "2024-01-15T09:30:00Z",
      "protocols": ["tcp", "udp"]
    }
  ],
  "total_files": 2,
  "total_size_mb": 8.1
}
```

---

### Get Replay Status

#### `GET /replay/{replay_id}/status`

Get the status of a running or completed replay.

**Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `replay_id` | string | Yes | Replay ID from replay response |

**Example Request**

```bash
curl "http://localhost:8003/replay/replay_20240115_103045/status"
```

**Response**

```json
{
  "replay_id": "replay_20240115_103045",
  "status": "completed",
  "progress": {
    "packets_sent": 4500,
    "total_packets": 4500,
    "percentage": 100.0,
    "current_loop": 3,
    "total_loops": 3
  },
  "statistics": {
    "start_time": "2024-01-15T10:30:45Z",
    "end_time": "2024-01-15T10:31:30Z",
    "duration_seconds": 45.0,
    "packets_per_second": 100.0
  },
  "errors": []
}
```

---

### Stop Replay

#### `POST /replay/{replay_id}/stop`

Stop a running replay operation.

**Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `replay_id` | string | Yes | Replay ID to stop |

**Response**

```json
{
  "status": "success",
  "message": "Replay stopped",
  "replay_id": "replay_20240115_103045",
  "packets_sent": 2250,
  "stopped_at": "2024-01-15T10:31:00Z"
}
```

## Traffic Generation Patterns

### Attack Types

| Attack Type | Description | Characteristics |
|-------------|-------------|-----------------|
| `port_scan` | Port scanning behavior | High connection attempts, multiple ports |
| `ddos` | Distributed denial of service | High packet rate, multiple sources |
| `malware` | Malware communication | Suspicious payloads, C&C patterns |
| `data_exfiltration` | Data theft patterns | Large outbound transfers |
| `brute_force` | Login attempts | Repeated authentication failures |
| `sql_injection` | Database attacks | Malicious SQL in HTTP requests |

### Protocol Support

| Protocol | Port Range | Description |
|----------|------------|-------------|
| `tcp` | 1-65535 | TCP connections and data transfer |
| `udp` | 1-65535 | UDP datagrams and services |
| `icmp` | N/A | ICMP messages and ping traffic |
| `http` | 80, 8080 | HTTP web traffic |
| `https` | 443, 8443 | HTTPS encrypted web traffic |
| `dns` | 53 | DNS queries and responses |
| `ssh` | 22 | SSH connection attempts |
| `ftp` | 21 | FTP file transfers |

## Configuration Options

### Replay Speed Settings

| Speed | Description | Use Case |
|-------|-------------|----------|
| 0.1 | Very slow (10x slower) | Detailed analysis |
| 0.5 | Half speed | Careful observation |
| 1.0 | Original timing | Realistic simulation |
| 2.0 | Double speed | Faster testing |
| 5.0 | 5x faster | Quick validation |
| 10.0 | Maximum speed | Stress testing |

### Packet Filters

The service supports Berkeley Packet Filter (BPF) syntax:

```bash
# TCP traffic only
"tcp"

# HTTP and HTTPS traffic
"tcp port 80 or tcp port 443"

# Specific IP address
"host 192.168.1.100"

# Port range
"portrange 1000-2000"

# Complex filter
"tcp and (port 80 or port 443) and host 192.168.1.0/24"
```

## Error Handling

### Common Errors

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `PCAP_NOT_FOUND` | 404 | PCAP file does not exist |
| `INVALID_PCAP` | 400 | PCAP file is corrupted or invalid |
| `REPLAY_FAILED` | 500 | Error during traffic replay |
| `GENERATION_FAILED` | 500 | Error during traffic generation |
| `INVALID_FILTER` | 400 | BPF filter syntax error |
| `INTERFACE_ERROR` | 500 | Network interface not available |

### Error Response Format

```json
{
  "status": "error",
  "message": "PCAP file not found: invalid_traffic.pcap",
  "error_code": "PCAP_NOT_FOUND",
  "details": {
    "requested_file": "invalid_traffic.pcap",
    "available_files": ["demo_traffic.pcap", "attack_samples.pcap"],
    "search_path": "/data/pcaps/"
  }
}
```

## Performance Specifications

### Replay Performance
- **Maximum Packet Rate**: 10,000 packets/second
- **File Size Limit**: 1GB PCAP files
- **Concurrent Replays**: Up to 5 simultaneous
- **Memory Usage**: ~50MB per active replay

### Generation Performance
- **Generation Rate**: 1,000-10,000 packets/second
- **Maximum Duration**: 1 hour continuous generation
- **Output File Size**: Up to 10GB
- **Memory Usage**: ~100MB during generation

## Rate Limits

- **Replay Traffic**: 10 requests per hour
- **Generate Traffic**: 5 requests per hour
- **List PCAP Files**: 60 requests per hour
- **Status Check**: 300 requests per hour

## Examples

### Python Client Example

```python
import requests
import time

class TrafficReplay:
    def __init__(self, base_url="http://localhost:8003"):
        self.base_url = base_url
    
    def replay_pcap(self, pcap_file, speed=1.0, loops=1):
        """Replay a PCAP file"""
        response = requests.post(
            f"{self.base_url}/replay",
            json={
                "pcap_file": pcap_file,
                "replay_speed": speed,
                "loop_count": loops
            }
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            error = response.json()
            raise Exception(f"Replay failed: {error['message']}")
    
    def generate_traffic(self, duration=60, pps=100, attack_ratio=0.3):
        """Generate synthetic traffic"""
        response = requests.post(
            f"{self.base_url}/generate",
            json={
                "duration_seconds": duration,
                "packets_per_second": pps,
                "attack_ratio": attack_ratio,
                "traffic_type": "mixed",
                "attack_types": ["port_scan", "ddos"]
            }
        )
        
        return response.json()
    
    def list_pcaps(self):
        """List available PCAP files"""
        response = requests.get(f"{self.base_url}/pcaps")
        return response.json()

# Usage example
replay = TrafficReplay()

# List available files
files = replay.list_pcaps()
print(f"Available PCAP files: {len(files['pcap_files'])}")

# Replay traffic at double speed
result = replay.replay_pcap("demo_traffic.pcap", speed=2.0, loops=2)
print(f"Replayed {result['statistics']['packets_sent']} packets")

# Generate synthetic attack traffic
gen_result = replay.generate_traffic(duration=120, pps=200, attack_ratio=0.5)
print(f"Generated {gen_result['statistics']['total_packets']} packets")
print(f"Output file: {gen_result['output_file']}")
```

### JavaScript Client Example

```javascript
class TrafficReplay {
  constructor(baseUrl = 'http://localhost:8003') {
    this.baseUrl = baseUrl;
  }
  
  async replayPcap(pcapFile, options = {}) {
    const defaultOptions = {
      replay_speed: 1.0,
      loop_count: 1,
      packet_filter: ""
    };
    
    const config = { ...defaultOptions, ...options, pcap_file: pcapFile };
    
    try {
      const response = await fetch(`${this.baseUrl}/replay`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config)
      });
      
      const result = await response.json();
      
      if (response.ok) {
        return result;
      } else {
        throw new Error(result.message);
      }
    } catch (error) {
      console.error('Replay failed:', error);
      throw error;
    }
  }
  
  async generateTraffic(config) {
    const defaultConfig = {
      traffic_type: "mixed",
      duration_seconds: 60,
      packets_per_second: 100,
      attack_ratio: 0.3
    };
    
    const finalConfig = { ...defaultConfig, ...config };
    
    const response = await fetch(`${this.baseUrl}/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(finalConfig)
    });
    
    return response.json();
  }
  
  async listPcaps() {
    const response = await fetch(`${this.baseUrl}/pcaps`);
    return response.json();
  }
}

// Usage
const replay = new TrafficReplay();

// Replay with custom settings
replay.replayPcap('demo_traffic.pcap', {
  replay_speed: 1.5,
  loop_count: 3,
  packet_filter: 'tcp port 80'
})
.then(result => {
  console.log(`Replay completed: ${result.statistics.packets_sent} packets`);
  console.log(`Duration: ${result.statistics.duration_seconds}s`);
})
.catch(error => {
  console.error('Replay error:', error);
});

// Generate synthetic traffic
replay.generateTraffic({
  duration_seconds: 180,
  packets_per_second: 150,
  attack_ratio: 0.4,
  attack_types: ['port_scan', 'ddos', 'malware']
})
.then(result => {
  console.log(`Generated ${result.statistics.total_packets} packets`);
  console.log(`File: ${result.output_file} (${result.statistics.file_size_mb}MB)`);
});
```

## Integration Notes

- The service integrates with the Feature Extractor for processing generated traffic
- Generated PCAP files are automatically saved to `/data/pcaps/` directory
- Replay operations can be monitored in real-time via status endpoints
- The service supports both synchronous and asynchronous operation modes
- Network interface selection depends on Docker container networking configuration
- Generated traffic includes realistic timing and payload patterns for accurate testing
