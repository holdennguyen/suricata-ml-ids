"""
Feature Engine for Network Traffic Analysis
Extracts 25+ features from network packets for ML training
"""

import logging
from typing import Dict, List, Any, Optional
import numpy as np
from collections import defaultdict, Counter
import time

logger = logging.getLogger(__name__)

class FeatureEngine:
    """
    Extracts comprehensive network features from packet data
    Designed to capture both normal and malicious traffic patterns
    """
    
    def __init__(self):
        self.feature_names = self._get_feature_names()
    
    def _get_feature_names(self) -> List[str]:
        """Return list of all feature names"""
        return [
            # Basic packet statistics
            'total_packets',
            'total_bytes',
            'avg_packet_size',
            'packet_size_variance',
            'duration',
            
            # Protocol distribution
            'tcp_packets',
            'udp_packets',
            'icmp_packets',
            'other_packets',
            'tcp_ratio',
            'udp_ratio',
            'icmp_ratio',
            
            # TCP specific features
            'tcp_syn_count',
            'tcp_fin_count',
            'tcp_rst_count',
            'tcp_psh_count',
            'tcp_ack_count',
            'tcp_urg_count',
            'tcp_syn_ratio',
            
            # Flow characteristics
            'unique_src_ips',
            'unique_dst_ips',
            'unique_src_ports',
            'unique_dst_ports',
            'src_ip_entropy',
            'dst_ip_entropy',
            
            # Timing features
            'packets_per_second',
            'bytes_per_second',
            'inter_packet_time_avg',
            'inter_packet_time_std',
            
            # Port analysis
            'well_known_ports',
            'high_ports',
            'port_entropy',
            
            # Payload features
            'avg_payload_size',
            'payload_entropy',
            'zero_payload_packets',
            
            # Anomaly indicators
            'fragmented_packets',
            'malformed_packets',
            'suspicious_flags',
            
            # Application layer
            'http_requests',
            'dns_queries',
            'tls_handshakes'
        ]
    
    def get_feature_names(self) -> List[str]:
        """Public method to get feature names"""
        return self.feature_names
    
    async def extract_features(self, packets: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Extract all features from packet list
        
        Args:
            packets: List of packet dictionaries from PCAP processor
            
        Returns:
            Dictionary of feature names and values
        """
        if not packets:
            return {name: 0.0 for name in self.feature_names}
        
        try:
            features = {}
            
            # Basic statistics
            features.update(self._extract_basic_stats(packets))
            
            # Protocol analysis
            features.update(self._extract_protocol_features(packets))
            
            # TCP analysis
            features.update(self._extract_tcp_features(packets))
            
            # Flow analysis
            features.update(self._extract_flow_features(packets))
            
            # Timing analysis
            features.update(self._extract_timing_features(packets))
            
            # Port analysis
            features.update(self._extract_port_features(packets))
            
            # Payload analysis
            features.update(self._extract_payload_features(packets))
            
            # Anomaly detection features
            features.update(self._extract_anomaly_features(packets))
            
            # Application layer features
            features.update(self._extract_application_features(packets))
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features: {str(e)}")
            return {name: 0.0 for name in self.feature_names}
    
    def _extract_basic_stats(self, packets: List[Dict]) -> Dict[str, float]:
        """Extract basic packet statistics"""
        if not packets:
            return {
                'total_packets': 0.0,
                'total_bytes': 0.0,
                'avg_packet_size': 0.0,
                'packet_size_variance': 0.0,
                'duration': 0.0
            }
        
        sizes = [p.get('length', 0) for p in packets]
        timestamps = [p.get('timestamp', 0) for p in packets if p.get('timestamp')]
        
        total_packets = len(packets)
        total_bytes = sum(sizes)
        avg_size = np.mean(sizes) if sizes else 0.0
        size_variance = np.var(sizes) if len(sizes) > 1 else 0.0
        
        duration = 0.0
        if len(timestamps) > 1:
            duration = max(timestamps) - min(timestamps)
        
        return {
            'total_packets': float(total_packets),
            'total_bytes': float(total_bytes),
            'avg_packet_size': avg_size,
            'packet_size_variance': size_variance,
            'duration': duration
        }
    
    def _extract_protocol_features(self, packets: List[Dict]) -> Dict[str, float]:
        """Extract protocol distribution features"""
        protocol_counts = Counter()
        
        for packet in packets:
            protocol = packet.get('protocol', 'other').lower()
            protocol_counts[protocol] += 1
        
        total = len(packets)
        if total == 0:
            return {
                'tcp_packets': 0.0, 'udp_packets': 0.0, 'icmp_packets': 0.0,
                'other_packets': 0.0, 'tcp_ratio': 0.0, 'udp_ratio': 0.0,
                'icmp_ratio': 0.0
            }
        
        tcp_count = protocol_counts.get('tcp', 0)
        udp_count = protocol_counts.get('udp', 0)
        icmp_count = protocol_counts.get('icmp', 0)
        other_count = total - tcp_count - udp_count - icmp_count
        
        return {
            'tcp_packets': float(tcp_count),
            'udp_packets': float(udp_count),
            'icmp_packets': float(icmp_count),
            'other_packets': float(other_count),
            'tcp_ratio': tcp_count / total,
            'udp_ratio': udp_count / total,
            'icmp_ratio': icmp_count / total
        }
    
    def _extract_tcp_features(self, packets: List[Dict]) -> Dict[str, float]:
        """Extract TCP-specific features"""
        tcp_packets = [p for p in packets if p.get('protocol', '').lower() == 'tcp']
        
        if not tcp_packets:
            return {
                'tcp_syn_count': 0.0, 'tcp_fin_count': 0.0, 'tcp_rst_count': 0.0,
                'tcp_psh_count': 0.0, 'tcp_ack_count': 0.0, 'tcp_urg_count': 0.0,
                'tcp_syn_ratio': 0.0
            }
        
        flag_counts = {
            'syn': 0, 'fin': 0, 'rst': 0, 'psh': 0, 'ack': 0, 'urg': 0
        }
        
        for packet in tcp_packets:
            flags = packet.get('tcp_flags', {})
            for flag in flag_counts:
                if flags.get(flag, False):
                    flag_counts[flag] += 1
        
        total_tcp = len(tcp_packets)
        
        return {
            'tcp_syn_count': float(flag_counts['syn']),
            'tcp_fin_count': float(flag_counts['fin']),
            'tcp_rst_count': float(flag_counts['rst']),
            'tcp_psh_count': float(flag_counts['psh']),
            'tcp_ack_count': float(flag_counts['ack']),
            'tcp_urg_count': float(flag_counts['urg']),
            'tcp_syn_ratio': flag_counts['syn'] / total_tcp if total_tcp > 0 else 0.0
        }
    
    def _extract_flow_features(self, packets: List[Dict]) -> Dict[str, float]:
        """Extract network flow characteristics"""
        src_ips = set()
        dst_ips = set()
        src_ports = set()
        dst_ports = set()
        
        for packet in packets:
            if 'src_ip' in packet:
                src_ips.add(packet['src_ip'])
            if 'dst_ip' in packet:
                dst_ips.add(packet['dst_ip'])
            if 'src_port' in packet:
                src_ports.add(packet['src_port'])
            if 'dst_port' in packet:
                dst_ports.add(packet['dst_port'])
        
        # Calculate entropy
        src_ip_entropy = self._calculate_entropy([p.get('src_ip') for p in packets])
        dst_ip_entropy = self._calculate_entropy([p.get('dst_ip') for p in packets])
        
        return {
            'unique_src_ips': float(len(src_ips)),
            'unique_dst_ips': float(len(dst_ips)),
            'unique_src_ports': float(len(src_ports)),
            'unique_dst_ports': float(len(dst_ports)),
            'src_ip_entropy': src_ip_entropy,
            'dst_ip_entropy': dst_ip_entropy
        }
    
    def _extract_timing_features(self, packets: List[Dict]) -> Dict[str, float]:
        """Extract timing-based features"""
        timestamps = [p.get('timestamp', 0) for p in packets if p.get('timestamp')]
        
        if len(timestamps) < 2:
            return {
                'packets_per_second': 0.0,
                'bytes_per_second': 0.0,
                'inter_packet_time_avg': 0.0,
                'inter_packet_time_std': 0.0
            }
        
        duration = max(timestamps) - min(timestamps)
        total_bytes = sum(p.get('length', 0) for p in packets)
        
        # Calculate inter-packet times
        inter_times = []
        for i in range(1, len(timestamps)):
            inter_times.append(timestamps[i] - timestamps[i-1])
        
        packets_per_sec = len(packets) / duration if duration > 0 else 0.0
        bytes_per_sec = total_bytes / duration if duration > 0 else 0.0
        
        return {
            'packets_per_second': packets_per_sec,
            'bytes_per_second': bytes_per_sec,
            'inter_packet_time_avg': np.mean(inter_times) if inter_times else 0.0,
            'inter_packet_time_std': np.std(inter_times) if inter_times else 0.0
        }
    
    def _extract_port_features(self, packets: List[Dict]) -> Dict[str, float]:
        """Extract port-based features"""
        ports = []
        well_known_count = 0
        high_port_count = 0
        
        for packet in packets:
            src_port = packet.get('src_port')
            dst_port = packet.get('dst_port')
            
            for port in [src_port, dst_port]:
                if port is not None:
                    ports.append(port)
                    if port <= 1023:
                        well_known_count += 1
                    elif port >= 32768:
                        high_port_count += 1
        
        port_entropy = self._calculate_entropy(ports)
        
        return {
            'well_known_ports': float(well_known_count),
            'high_ports': float(high_port_count),
            'port_entropy': port_entropy
        }
    
    def _extract_payload_features(self, packets: List[Dict]) -> Dict[str, float]:
        """Extract payload-based features"""
        payload_sizes = []
        zero_payload_count = 0
        total_entropy = 0.0
        entropy_count = 0
        
        for packet in packets:
            payload = packet.get('payload', b'')
            payload_size = len(payload) if payload else 0
            payload_sizes.append(payload_size)
            
            if payload_size == 0:
                zero_payload_count += 1
            else:
                # Calculate payload entropy
                if isinstance(payload, (bytes, bytearray)):
                    byte_counts = Counter(payload)
                    entropy = self._calculate_entropy_from_counts(byte_counts, payload_size)
                    total_entropy += entropy
                    entropy_count += 1
        
        avg_payload_size = np.mean(payload_sizes) if payload_sizes else 0.0
        avg_entropy = total_entropy / entropy_count if entropy_count > 0 else 0.0
        
        return {
            'avg_payload_size': avg_payload_size,
            'payload_entropy': avg_entropy,
            'zero_payload_packets': float(zero_payload_count)
        }
    
    def _extract_anomaly_features(self, packets: List[Dict]) -> Dict[str, float]:
        """Extract features indicating potential anomalies"""
        fragmented_count = 0
        malformed_count = 0
        suspicious_flags_count = 0
        
        for packet in packets:
            # Check for fragmentation
            if packet.get('fragmented', False):
                fragmented_count += 1
            
            # Check for malformed packets (basic heuristic)
            if packet.get('length', 0) < 20:  # Minimum IP header size
                malformed_count += 1
            
            # Check for suspicious TCP flag combinations
            tcp_flags = packet.get('tcp_flags', {})
            if tcp_flags.get('syn') and tcp_flags.get('fin'):
                suspicious_flags_count += 1
            if tcp_flags.get('syn') and tcp_flags.get('rst'):
                suspicious_flags_count += 1
        
        return {
            'fragmented_packets': float(fragmented_count),
            'malformed_packets': float(malformed_count),
            'suspicious_flags': float(suspicious_flags_count)
        }
    
    def _extract_application_features(self, packets: List[Dict]) -> Dict[str, float]:
        """Extract application layer features"""
        http_count = 0
        dns_count = 0
        tls_count = 0
        
        for packet in packets:
            dst_port = packet.get('dst_port', 0)
            src_port = packet.get('src_port', 0)
            
            # HTTP detection (basic)
            if dst_port in [80, 8080] or src_port in [80, 8080]:
                http_count += 1
            
            # DNS detection
            if dst_port == 53 or src_port == 53:
                dns_count += 1
            
            # TLS detection
            if dst_port in [443, 993, 995] or src_port in [443, 993, 995]:
                tls_count += 1
        
        return {
            'http_requests': float(http_count),
            'dns_queries': float(dns_count),
            'tls_handshakes': float(tls_count)
        }
    
    def _calculate_entropy(self, values: List[Any]) -> float:
        """Calculate Shannon entropy of a list of values"""
        if not values:
            return 0.0
        
        # Filter out None values
        values = [v for v in values if v is not None]
        if not values:
            return 0.0
        
        value_counts = Counter(values)
        total = len(values)
        
        return self._calculate_entropy_from_counts(value_counts, total)
    
    def _calculate_entropy_from_counts(self, counts: Counter, total: int) -> float:
        """Calculate entropy from value counts"""
        if total == 0:
            return 0.0
        
        entropy = 0.0
        for count in counts.values():
            if count > 0:
                probability = count / total
                entropy -= probability * np.log2(probability)
        
        return entropy
