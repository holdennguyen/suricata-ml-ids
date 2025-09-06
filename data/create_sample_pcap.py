#!/usr/bin/env python3
import os
os.environ['SCAPY_USE_PCAPY'] = '0'

from scapy.all import *
from scapy.layers.inet import IP, TCP, UDP, ICMP
import random

def create_sample_pcap():
    packets = []
    
    # Generate normal HTTP traffic
    for i in range(50):
        pkt = IP(src=f"192.168.1.{random.randint(10, 50)}", 
                dst="93.184.216.34") / TCP(sport=random.randint(32768, 65535), 
                                          dport=80) / "GET / HTTP/1.1\r\nHost: example.com\r\n\r\n"
        packets.append(pkt)
    
    # Generate DNS queries
    for i in range(20):
        pkt = IP(src=f"192.168.1.{random.randint(10, 50)}", 
                dst="8.8.8.8") / UDP(sport=random.randint(32768, 65535), 
                                    dport=53) / "DNS Query"
        packets.append(pkt)
    
    # Generate suspicious port scan
    src_ip = "10.0.0.100"
    for port in range(20, 100, 5):
        pkt = IP(src=src_ip, dst="192.168.1.10") / TCP(sport=54321, dport=port, flags="S")
        packets.append(pkt)
    
    # Save to PCAP file
    wrpcap('pcaps/samples/demo_traffic.pcap', packets)
    print(f"Created sample PCAP with {len(packets)} packets")

if __name__ == "__main__":
    create_sample_pcap()
