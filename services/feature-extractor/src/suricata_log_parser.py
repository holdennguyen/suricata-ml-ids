"""
Suricata Log Parser for Feature Enhancement
Parses Suricata EVE JSON logs to enhance feature extraction
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class SuricataLogParser:
    """
    Parses Suricata EVE JSON logs and extracts relevant information
    for enhancing ML feature extraction
    """
    
    def __init__(self):
        self.supported_event_types = [
            'alert', 'http', 'dns', 'tls', 'ssh', 'smtp', 'flow', 'netflow', 'stats'
        ]
    
    async def parse_eve_log(self, log_path: Path) -> List[Dict[str, Any]]:
        """
        Parse Suricata EVE JSON log file
        
        Args:
            log_path: Path to the EVE JSON log file
            
        Returns:
            List of parsed log events
        """
        try:
            if not log_path.exists():
                logger.warning(f"EVE log file not found: {log_path}")
                return []
            
            events = []
            
            with open(log_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        event = json.loads(line)
                        parsed_event = self._parse_event(event)
                        if parsed_event:
                            events.append(parsed_event)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Invalid JSON at line {line_num}: {e}")
                        continue
                    except Exception as e:
                        logger.warning(f"Error parsing event at line {line_num}: {e}")
                        continue
            
            logger.info(f"Parsed {len(events)} events from {log_path}")
            return events
            
        except Exception as e:
            logger.error(f"Error parsing EVE log {log_path}: {str(e)}")
            return []
    
    def _parse_event(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse a single Suricata event
        
        Args:
            event: Raw event dictionary from JSON
            
        Returns:
            Parsed event dictionary or None if invalid
        """
        try:
            event_type = event.get('event_type')
            if event_type not in self.supported_event_types:
                return None
            
            parsed = {
                'timestamp': event.get('timestamp'),
                'event_type': event_type,
                'src_ip': event.get('src_ip'),
                'dest_ip': event.get('dest_ip'),
                'src_port': event.get('src_port'),
                'dest_port': event.get('dest_port'),
                'proto': event.get('proto'),
                'flow_id': event.get('flow_id'),
                'community_id': event.get('community_id')
            }
            
            # Parse event-specific data
            if event_type == 'alert':
                parsed.update(self._parse_alert(event))
            elif event_type == 'http':
                parsed.update(self._parse_http(event))
            elif event_type == 'dns':
                parsed.update(self._parse_dns(event))
            elif event_type == 'tls':
                parsed.update(self._parse_tls(event))
            elif event_type == 'ssh':
                parsed.update(self._parse_ssh(event))
            elif event_type == 'flow':
                parsed.update(self._parse_flow(event))
            elif event_type == 'netflow':
                parsed.update(self._parse_netflow(event))
            
            return parsed
            
        except Exception as e:
            logger.debug(f"Error parsing individual event: {e}")
            return None
    
    def _parse_alert(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Parse alert event"""
        alert = event.get('alert', {})
        
        return {
            'alert_signature': alert.get('signature'),
            'alert_category': alert.get('category'),
            'alert_severity': alert.get('severity'),
            'alert_gid': alert.get('gid'),
            'alert_signature_id': alert.get('signature_id'),
            'alert_rev': alert.get('rev'),
            'alert_action': alert.get('action'),
            'payload': event.get('payload'),
            'payload_printable': event.get('payload_printable'),
            'packet': event.get('packet')
        }
    
    def _parse_http(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Parse HTTP event"""
        http = event.get('http', {})
        
        return {
            'http_hostname': http.get('hostname'),
            'http_url': http.get('url'),
            'http_user_agent': http.get('http_user_agent'),
            'http_method': http.get('http_method'),
            'http_protocol': http.get('protocol'),
            'http_status': http.get('status'),
            'http_length': http.get('length'),
            'http_content_type': http.get('http_content_type'),
            'http_refer': http.get('http_refer')
        }
    
    def _parse_dns(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Parse DNS event"""
        dns = event.get('dns', {})
        
        return {
            'dns_query': dns.get('query'),
            'dns_type': dns.get('type'),
            'dns_id': dns.get('id'),
            'dns_rcode': dns.get('rcode'),
            'dns_rrname': dns.get('rrname'),
            'dns_rrtype': dns.get('rrtype'),
            'dns_rdata': dns.get('rdata'),
            'dns_ttl': dns.get('ttl')
        }
    
    def _parse_tls(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Parse TLS event"""
        tls = event.get('tls', {})
        
        return {
            'tls_subject': tls.get('subject'),
            'tls_issuer': tls.get('issuer'),
            'tls_serial': tls.get('serial'),
            'tls_fingerprint': tls.get('fingerprint'),
            'tls_version': tls.get('version'),
            'tls_not_before': tls.get('notbefore'),
            'tls_not_after': tls.get('notafter'),
            'tls_ja3': tls.get('ja3', {}).get('hash') if tls.get('ja3') else None,
            'tls_ja3s': tls.get('ja3s', {}).get('hash') if tls.get('ja3s') else None
        }
    
    def _parse_ssh(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Parse SSH event"""
        ssh = event.get('ssh', {})
        
        return {
            'ssh_client_software': ssh.get('client', {}).get('software_version'),
            'ssh_server_software': ssh.get('server', {}).get('software_version'),
            'ssh_client_proto': ssh.get('client', {}).get('proto_version'),
            'ssh_server_proto': ssh.get('server', {}).get('proto_version')
        }
    
    def _parse_flow(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Parse flow event"""
        flow = event.get('flow', {})
        
        return {
            'flow_pkts_toserver': flow.get('pkts_toserver'),
            'flow_pkts_toclient': flow.get('pkts_toclient'),
            'flow_bytes_toserver': flow.get('bytes_toserver'),
            'flow_bytes_toclient': flow.get('bytes_toclient'),
            'flow_start': flow.get('start'),
            'flow_end': flow.get('end'),
            'flow_age': flow.get('age'),
            'flow_state': flow.get('state'),
            'flow_reason': flow.get('reason')
        }
    
    def _parse_netflow(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Parse netflow event"""
        netflow = event.get('netflow', {})
        
        return {
            'netflow_pkts': netflow.get('pkts'),
            'netflow_bytes': netflow.get('bytes'),
            'netflow_start': netflow.get('start'),
            'netflow_end': netflow.get('end'),
            'netflow_age': netflow.get('age')
        }
    
    async def get_alerts_for_timerange(
        self, 
        log_path: Path, 
        start_time: datetime, 
        end_time: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get alerts within a specific time range
        
        Args:
            log_path: Path to EVE log file
            start_time: Start of time range
            end_time: End of time range
            
        Returns:
            List of alerts within the time range
        """
        try:
            events = await self.parse_eve_log(log_path)
            alerts = []
            
            for event in events:
                if event.get('event_type') != 'alert':
                    continue
                
                timestamp_str = event.get('timestamp')
                if not timestamp_str:
                    continue
                
                try:
                    # Parse Suricata timestamp format
                    event_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    
                    if start_time <= event_time <= end_time:
                        alerts.append(event)
                        
                except ValueError as e:
                    logger.debug(f"Error parsing timestamp {timestamp_str}: {e}")
                    continue
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting alerts for timerange: {str(e)}")
            return []
    
    async def get_event_statistics(self, log_path: Path) -> Dict[str, Any]:
        """
        Get statistics about events in the log file
        
        Args:
            log_path: Path to EVE log file
            
        Returns:
            Dictionary with event statistics
        """
        try:
            events = await self.parse_eve_log(log_path)
            
            if not events:
                return {'error': 'No events found in log file'}
            
            # Count events by type
            event_counts = {}
            alert_severities = {}
            protocols = {}
            
            for event in events:
                event_type = event.get('event_type', 'unknown')
                event_counts[event_type] = event_counts.get(event_type, 0) + 1
                
                # Count alert severities
                if event_type == 'alert':
                    severity = event.get('alert_severity', 'unknown')
                    alert_severities[severity] = alert_severities.get(severity, 0) + 1
                
                # Count protocols
                proto = event.get('proto', 'unknown')
                protocols[proto] = protocols.get(proto, 0) + 1
            
            # Get time range
            timestamps = [e.get('timestamp') for e in events if e.get('timestamp')]
            time_range = {}
            
            if timestamps:
                try:
                    parsed_times = []
                    for ts in timestamps:
                        try:
                            parsed_times.append(datetime.fromisoformat(ts.replace('Z', '+00:00')))
                        except ValueError:
                            continue
                    
                    if parsed_times:
                        time_range = {
                            'start': min(parsed_times).isoformat(),
                            'end': max(parsed_times).isoformat(),
                            'duration_seconds': (max(parsed_times) - min(parsed_times)).total_seconds()
                        }
                except Exception as e:
                    logger.debug(f"Error calculating time range: {e}")
            
            return {
                'total_events': len(events),
                'event_types': event_counts,
                'alert_severities': alert_severities,
                'protocols': protocols,
                'time_range': time_range
            }
            
        except Exception as e:
            logger.error(f"Error getting event statistics: {str(e)}")
            return {'error': str(e)}
