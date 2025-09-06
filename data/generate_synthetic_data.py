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
