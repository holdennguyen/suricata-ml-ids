"""
PCAP Processor for Feature Extraction
Processes PCAP files and extracts packet information for feature engineering
"""

import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime

import scapy.all as scapy
from scapy.layers.inet import IP, TCP, UDP, ICMP
from scapy.layers.inet6 import IPv6
from scapy.layers.l2 import Ether

logger = logging.getLogger(__name__)

class PCAPProcessor:
    """
    Processes PCAP files and extracts structured packet information
    """
    
    def __init__(self):
        self.supported_formats = ['.pcap', '.pcapng']
    
    async def process_pcap(self, pcap_path: Path) -> List[Dict[str, Any]]:
        """
        Process a PCAP file and extract packet information
        
        Args:
            pcap_path: Path to the PCAP file
            
        Returns:
            List of packet dictionaries with extracted information
        """
        try:
            if not pcap_path.exists():
                raise FileNotFoundError(f"PCAP file not found: {pcap_path}")
            
            if pcap_path.suffix not in self.supported_formats:
                raise ValueError(f"Unsupported file format: {pcap_path.suffix}")
            
            logger.info(f"Processing PCAP file: {pcap_path}")
            
            # Read PCAP file using Scapy
            packets = scapy.rdpcap(str(pcap_path))
            
            # Process packets in batches to avoid memory issues
            batch_size = 1000
            processed_packets = []
            
            for i in range(0, len(packets), batch_size):
                batch = packets[i:i + batch_size]
                batch_processed = await self._process_packet_batch(batch)
                processed_packets.extend(batch_processed)
                
                # Log progress for large files
                if len(packets) > 10000:
                    progress = (i + len(batch)) / len(packets) * 100
                    logger.info(f"Processing progress: {progress:.1f}%")
            
            logger.info(f"Processed {len(processed_packets)} packets from {pcap_path}")
            return processed_packets
            
        except Exception as e:
            logger.error(f"Error processing PCAP file {pcap_path}: {str(e)}")
            raise
    
    async def _process_packet_batch(self, packets: List[scapy.Packet]) -> List[Dict[str, Any]]:
        """Process a batch of packets"""
        processed = []
        
        for packet in packets:
            try:
                packet_info = self._extract_packet_info(packet)
                if packet_info:
                    processed.append(packet_info)
            except Exception as e:
                logger.warning(f"Error processing packet: {str(e)}")
                continue
        
        return processed
    
    def _extract_packet_info(self, packet: scapy.Packet) -> Optional[Dict[str, Any]]:
        """
        Extract relevant information from a single packet
        
        Args:
            packet: Scapy packet object
            
        Returns:
            Dictionary with packet information or None if packet is invalid
        """
        try:
            packet_info = {
                'timestamp': float(packet.time),
                'length': len(packet),
                'protocol': 'other',
                'src_ip': None,
                'dst_ip': None,
                'src_port': None,
                'dst_port': None,
                'tcp_flags': {},
                'fragmented': False,
                'payload': b'',
                'ip_version': None
            }
            
            # Extract Ethernet layer info if present
            if packet.haslayer(Ether):
                ether = packet[Ether]
                packet_info['eth_src'] = ether.src
                packet_info['eth_dst'] = ether.dst
                packet_info['eth_type'] = ether.type
            
            # Extract IP layer information
            if packet.haslayer(IP):
                ip = packet[IP]
                packet_info['src_ip'] = ip.src
                packet_info['dst_ip'] = ip.dst
                packet_info['ip_version'] = ip.version
                packet_info['ttl'] = ip.ttl
                packet_info['ip_len'] = ip.len
                packet_info['fragmented'] = bool(ip.flags & 0x1) or (ip.frag > 0)
                
                # Determine protocol
                if packet.haslayer(TCP):
                    packet_info['protocol'] = 'tcp'
                elif packet.haslayer(UDP):
                    packet_info['protocol'] = 'udp'
                elif packet.haslayer(ICMP):
                    packet_info['protocol'] = 'icmp'
                else:
                    packet_info['protocol'] = f'ip_proto_{ip.proto}'
            
            elif packet.haslayer(IPv6):
                ipv6 = packet[IPv6]
                packet_info['src_ip'] = ipv6.src
                packet_info['dst_ip'] = ipv6.dst
                packet_info['ip_version'] = 6
                packet_info['hop_limit'] = ipv6.hlim
                
                # Determine protocol for IPv6
                if packet.haslayer(TCP):
                    packet_info['protocol'] = 'tcp'
                elif packet.haslayer(UDP):
                    packet_info['protocol'] = 'udp'
                elif packet.haslayer(ICMP):
                    packet_info['protocol'] = 'icmp'
                else:
                    packet_info['protocol'] = f'ipv6_nh_{ipv6.nh}'
            
            # Extract TCP information
            if packet.haslayer(TCP):
                tcp = packet[TCP]
                packet_info['src_port'] = tcp.sport
                packet_info['dst_port'] = tcp.dport
                packet_info['tcp_seq'] = tcp.seq
                packet_info['tcp_ack'] = tcp.ack
                packet_info['tcp_window'] = tcp.window
                
                # Extract TCP flags
                packet_info['tcp_flags'] = {
                    'fin': bool(tcp.flags & 0x01),
                    'syn': bool(tcp.flags & 0x02),
                    'rst': bool(tcp.flags & 0x04),
                    'psh': bool(tcp.flags & 0x08),
                    'ack': bool(tcp.flags & 0x10),
                    'urg': bool(tcp.flags & 0x20),
                    'ece': bool(tcp.flags & 0x40),
                    'cwr': bool(tcp.flags & 0x80)
                }
                
                # Extract payload
                if hasattr(tcp, 'payload') and tcp.payload:
                    packet_info['payload'] = bytes(tcp.payload)
            
            # Extract UDP information
            elif packet.haslayer(UDP):
                udp = packet[UDP]
                packet_info['src_port'] = udp.sport
                packet_info['dst_port'] = udp.dport
                packet_info['udp_len'] = udp.len
                
                # Extract payload
                if hasattr(udp, 'payload') and udp.payload:
                    packet_info['payload'] = bytes(udp.payload)
            
            # Extract ICMP information
            elif packet.haslayer(ICMP):
                icmp = packet[ICMP]
                packet_info['icmp_type'] = icmp.type
                packet_info['icmp_code'] = icmp.code
                
                # Extract payload
                if hasattr(icmp, 'payload') and icmp.payload:
                    packet_info['payload'] = bytes(icmp.payload)
            
            # Extract raw payload if not already extracted
            if not packet_info['payload'] and hasattr(packet, 'payload'):
                try:
                    packet_info['payload'] = bytes(packet.payload)
                except:
                    packet_info['payload'] = b''
            
            # Additional packet analysis
            packet_info.update(self._analyze_packet_anomalies(packet))
            
            return packet_info
            
        except Exception as e:
            logger.warning(f"Error extracting packet info: {str(e)}")
            return None
    
    def _analyze_packet_anomalies(self, packet: scapy.Packet) -> Dict[str, Any]:
        """
        Analyze packet for potential anomalies
        
        Args:
            packet: Scapy packet object
            
        Returns:
            Dictionary with anomaly indicators
        """
        anomalies = {
            'is_broadcast': False,
            'is_multicast': False,
            'has_options': False,
            'suspicious_size': False,
            'malformed_headers': False
        }
        
        try:
            # Check for broadcast/multicast
            if packet.haslayer(Ether):
                ether = packet[Ether]
                dst_mac = ether.dst.lower()
                if dst_mac == 'ff:ff:ff:ff:ff:ff':
                    anomalies['is_broadcast'] = True
                elif dst_mac.startswith('01:00:5e') or dst_mac.startswith('33:33'):
                    anomalies['is_multicast'] = True
            
            # Check for IP options
            if packet.haslayer(IP):
                ip = packet[IP]
                if ip.ihl > 5:  # IP header length > 20 bytes means options present
                    anomalies['has_options'] = True
                
                # Check for suspicious sizes
                if ip.len > 65535 or ip.len < 20:
                    anomalies['suspicious_size'] = True
                    anomalies['malformed_headers'] = True
            
            # Check for TCP options
            if packet.haslayer(TCP):
                tcp = packet[TCP]
                if tcp.dataofs > 5:  # TCP header length > 20 bytes means options
                    anomalies['has_options'] = True
            
            # Check for extremely small or large packets
            packet_len = len(packet)
            if packet_len < 14 or packet_len > 9000:  # Below Ethernet min or above jumbo
                anomalies['suspicious_size'] = True
            
        except Exception as e:
            logger.debug(f"Error analyzing packet anomalies: {str(e)}")
            anomalies['malformed_headers'] = True
        
        return anomalies
    
    async def get_pcap_summary(self, pcap_path: Path) -> Dict[str, Any]:
        """
        Get a summary of PCAP file without full processing
        
        Args:
            pcap_path: Path to PCAP file
            
        Returns:
            Dictionary with PCAP summary information
        """
        try:
            packets = scapy.rdpcap(str(pcap_path))
            
            if not packets:
                return {'error': 'No packets found in PCAP file'}
            
            # Basic statistics
            total_packets = len(packets)
            first_timestamp = float(packets[0].time)
            last_timestamp = float(packets[-1].time)
            duration = last_timestamp - first_timestamp
            
            # Protocol distribution (sample first 1000 packets for efficiency)
            sample_size = min(1000, total_packets)
            sample_packets = packets[:sample_size]
            
            protocol_counts = {'tcp': 0, 'udp': 0, 'icmp': 0, 'other': 0}
            
            for packet in sample_packets:
                if packet.haslayer(TCP):
                    protocol_counts['tcp'] += 1
                elif packet.haslayer(UDP):
                    protocol_counts['udp'] += 1
                elif packet.haslayer(ICMP):
                    protocol_counts['icmp'] += 1
                else:
                    protocol_counts['other'] += 1
            
            # Estimate full file distribution
            scale_factor = total_packets / sample_size
            for protocol in protocol_counts:
                protocol_counts[protocol] = int(protocol_counts[protocol] * scale_factor)
            
            return {
                'filename': pcap_path.name,
                'total_packets': total_packets,
                'duration_seconds': duration,
                'start_time': datetime.fromtimestamp(first_timestamp).isoformat(),
                'end_time': datetime.fromtimestamp(last_timestamp).isoformat(),
                'protocol_distribution': protocol_counts,
                'avg_packets_per_second': total_packets / duration if duration > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting PCAP summary for {pcap_path}: {str(e)}")
            return {'error': str(e)}
