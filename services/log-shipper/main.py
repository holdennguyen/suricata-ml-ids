#!/usr/bin/env python3
"""
Real-time Eve.json to Elasticsearch Streaming Service
This replaces Filebeat with a custom Python-based log shipper
"""

import json
import time
import asyncio
import aiofiles
from datetime import datetime
from pathlib import Path
from elasticsearch import AsyncElasticsearch
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EveLogHandler(FileSystemEventHandler):
    """Handles eve.json file changes and streams to Elasticsearch"""
    
    def __init__(self, es_client, index_prefix="suricata-events"):
        self.es_client = es_client
        self.index_prefix = index_prefix
        self.last_position = 0
        self.eve_file = Path("/var/log/suricata/eve.json")
        
    async def process_new_lines(self):
        """Process new lines from eve.json"""
        try:
            if not self.eve_file.exists():
                logger.warning(f"Eve file not found: {self.eve_file}")
                return
                
            current_size = self.eve_file.stat().st_size
            
            if current_size <= self.last_position:
                return  # No new data
                
            async with aiofiles.open(self.eve_file, 'r') as f:
                await f.seek(self.last_position)
                new_lines = await f.read()
                
            if not new_lines.strip():
                return
                
            # Process each line
            events = []
            for line in new_lines.strip().split('\n'):
                if line.strip():
                    try:
                        event = json.loads(line)
                        # Add metadata
                        event['@timestamp'] = event.get('timestamp', datetime.utcnow().isoformat() + 'Z')
                        event['logtype'] = 'suricata'
                        event['service'] = 'ids'
                        events.append(event)
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON decode error: {e}")
                        continue
            
            if events:
                await self.bulk_index(events)
                logger.info(f"Streamed {len(events)} events to Elasticsearch")
                
            self.last_position = current_size
            
        except Exception as e:
            logger.error(f"Error processing eve.json: {e}")
    
    async def bulk_index(self, events):
        """Bulk index events to Elasticsearch"""
        try:
            today = datetime.now().strftime("%Y.%m.%d")
            index_name = f"{self.index_prefix}-{today}"
            
            # Prepare bulk operations
            operations = []
            for event in events:
                operations.append({"index": {"_index": index_name}})
                operations.append(event)
            
            # Bulk index
            response = await self.es_client.bulk(operations=operations)
            
            if response.get('errors'):
                logger.error(f"Bulk indexing errors occurred for {len(events)} events")
                for item in response.get('items', []):
                    if 'index' in item and 'error' in item['index']:
                        logger.error(f"Detailed error: {item['index']['error']}")
            else:
                logger.info(f"✅ Successfully indexed {len(events)} events to {index_name}")
            
        except Exception as e:
            logger.error(f"Bulk indexing failed: {e}")
    
    def on_modified(self, event):
        """File system event handler"""
        if event.src_path.endswith('eve.json'):
            asyncio.create_task(self.process_new_lines())

async def main():
    """Main streaming service"""
    logger.info("🚀 Starting Eve.json Real-time Streaming Service")
    
    # Initialize Elasticsearch client
    es_client = AsyncElasticsearch(
        hosts=['http://elasticsearch:9200'],
        retry_on_timeout=True,
        max_retries=3
    )
    
    try:
        # Test connection
        await es_client.info()
        logger.info("✅ Connected to Elasticsearch")
    except Exception as e:
        logger.error(f"❌ Failed to connect to Elasticsearch: {e}")
        return
    
    # Initialize handler
    handler = EveLogHandler(es_client, "suricata-events")
    
    # Set up file watcher
    observer = Observer()
    observer.schedule(handler, path="/var/log/suricata", recursive=False)
    observer.start()
    
    logger.info("👁️  Watching /var/log/suricata/eve.json for changes...")
    
    try:
        # Process existing data first
        await handler.process_new_lines()
        
        # Keep running and periodically check for new data
        while True:
            await handler.process_new_lines()
            await asyncio.sleep(5)  # Check every 5 seconds
            
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down log shipper...")
    finally:
        observer.stop()
        observer.join()
        await es_client.close()

if __name__ == "__main__":
    asyncio.run(main())
