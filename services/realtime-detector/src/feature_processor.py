"""
Feature Processor for Real-time Detection
Handles feature processing and validation for real-time detection
"""

import logging
import numpy as np
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class FeatureProcessor:
    """
    Processes and validates features for real-time detection
    """
    
    def __init__(self):
        self.required_features = [
            'total_packets', 'total_bytes', 'avg_packet_size', 'duration',
            'tcp_ratio', 'udp_ratio', 'icmp_ratio', 'packets_per_second',
            'unique_src_ips', 'unique_dst_ips', 'tcp_syn_ratio',
            'well_known_ports', 'high_ports', 'payload_entropy',
            'suspicious_flags', 'http_requests', 'dns_queries', 'tls_handshakes'
        ]
        
        self.feature_ranges = {
            'total_packets': (0, 10000),
            'total_bytes': (0, 1000000),
            'avg_packet_size': (0, 1500),
            'duration': (0, 3600),
            'tcp_ratio': (0, 1),
            'udp_ratio': (0, 1),
            'icmp_ratio': (0, 1),
            'packets_per_second': (0, 1000),
            'unique_src_ips': (0, 1000),
            'unique_dst_ips': (0, 1000),
            'tcp_syn_ratio': (0, 1),
            'well_known_ports': (0, 100),
            'high_ports': (0, 1000),
            'payload_entropy': (0, 8),
            'suspicious_flags': (0, 100),
            'http_requests': (0, 1000),
            'dns_queries': (0, 1000),
            'tls_handshakes': (0, 1000)
        }
    
    async def process_features(self, features: Dict[str, float]) -> Dict[str, float]:
        """
        Process and validate features for detection
        """
        try:
            processed_features = {}
            
            # Process each required feature
            for feature_name in self.required_features:
                value = features.get(feature_name, 0.0)
                
                # Validate and clean the value
                processed_value = self._validate_and_clean_feature(feature_name, value)
                processed_features[feature_name] = processed_value
            
            # Add any additional features that might be useful
            for feature_name, value in features.items():
                if feature_name not in processed_features:
                    processed_value = self._validate_and_clean_feature(feature_name, value)
                    processed_features[feature_name] = processed_value
            
            logger.debug(f"Processed {len(processed_features)} features")
            
            return processed_features
            
        except Exception as e:
            logger.error(f"Error processing features: {str(e)}")
            raise
    
    def _validate_and_clean_feature(self, feature_name: str, value: Any) -> float:
        """
        Validate and clean a single feature value
        """
        try:
            # Convert to float
            if value is None:
                value = 0.0
            else:
                value = float(value)
            
            # Check for NaN or infinite values
            if np.isnan(value) or np.isinf(value):
                logger.warning(f"Invalid value for {feature_name}: {value}, using 0.0")
                return 0.0
            
            # Apply range constraints if defined
            if feature_name in self.feature_ranges:
                min_val, max_val = self.feature_ranges[feature_name]
                if value < min_val:
                    value = min_val
                elif value > max_val:
                    value = max_val
            
            return value
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Error processing feature {feature_name}: {e}, using 0.0")
            return 0.0
