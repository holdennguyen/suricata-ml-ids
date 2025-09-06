"""
Pydantic models for Feature Extractor Service API
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from pathlib import Path

class FeatureExtractionRequest(BaseModel):
    """Request model for feature extraction"""
    pcap_filename: str = Field(..., description="Name of the PCAP file to process")
    include_payload: bool = Field(default=False, description="Whether to include payload analysis")
    output_format: str = Field(default="csv", description="Output format (csv, json)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "pcap_filename": "traffic_sample.pcap",
                "include_payload": True,
                "output_format": "csv"
            }
        }

class FeatureExtractionResponse(BaseModel):
    """Response model for feature extraction"""
    pcap_filename: str = Field(..., description="Name of the processed PCAP file")
    output_filename: str = Field(..., description="Name of the generated feature file")
    feature_count: int = Field(..., description="Number of features extracted")
    features: Dict[str, float] = Field(..., description="Dictionary of extracted features")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "pcap_filename": "traffic_sample.pcap",
                "output_filename": "traffic_sample_features.csv",
                "feature_count": 42,
                "features": {
                    "total_packets": 1500.0,
                    "total_bytes": 2048000.0,
                    "tcp_ratio": 0.75,
                    "avg_packet_size": 1365.33
                },
                "processing_time": 2.45
            }
        }

class BatchExtractionRequest(BaseModel):
    """Request model for batch feature extraction"""
    pcap_directory: Optional[str] = Field(None, description="Directory containing PCAP files")
    file_pattern: str = Field(default="*.pcap", description="File pattern to match")
    include_payload: bool = Field(default=False, description="Whether to include payload analysis")
    output_format: str = Field(default="csv", description="Output format (csv, json)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "pcap_directory": "/app/pcaps",
                "file_pattern": "*.pcap",
                "include_payload": False,
                "output_format": "csv"
            }
        }

class BatchExtractionResponse(BaseModel):
    """Response model for batch feature extraction"""
    total_files: int = Field(..., description="Total number of files processed")
    successful: int = Field(..., description="Number of successfully processed files")
    failed: int = Field(..., description="Number of failed files")
    results: List[Dict[str, Any]] = Field(..., description="List of processing results")
    total_processing_time: Optional[float] = Field(None, description="Total processing time")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_files": 5,
                "successful": 4,
                "failed": 1,
                "results": [
                    {
                        "pcap_filename": "sample1.pcap",
                        "status": "success",
                        "feature_count": 42,
                        "output_filename": "sample1_features.csv"
                    },
                    {
                        "pcap_filename": "sample2.pcap",
                        "status": "failed",
                        "error": "File corrupted"
                    }
                ],
                "total_processing_time": 12.34
            }
        }

class FeatureFileInfo(BaseModel):
    """Information about a feature file"""
    filename: str = Field(..., description="Name of the feature file")
    feature_count: int = Field(..., description="Number of features in the file")
    sample_count: int = Field(..., description="Number of samples/rows in the file")
    created_timestamp: float = Field(..., description="File creation timestamp")
    file_size: int = Field(..., description="File size in bytes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "filename": "traffic_features.csv",
                "feature_count": 42,
                "sample_count": 1500,
                "created_timestamp": 1699123456.789,
                "file_size": 204800
            }
        }

class ServiceStats(BaseModel):
    """Service statistics model"""
    pcap_files_available: int = Field(..., description="Number of PCAP files available")
    feature_files_generated: int = Field(..., description="Number of feature files generated")
    total_packets_processed: int = Field(default=0, description="Total packets processed")
    total_processing_time: float = Field(default=0.0, description="Total processing time")
    service_uptime: str = Field(..., description="Service uptime")
    supported_features: List[str] = Field(..., description="List of supported feature names")
    
    class Config:
        json_schema_extra = {
            "example": {
                "pcap_files_available": 10,
                "feature_files_generated": 8,
                "total_packets_processed": 15000,
                "total_processing_time": 45.67,
                "service_uptime": "2h 15m 30s",
                "supported_features": [
                    "total_packets", "total_bytes", "tcp_ratio", "avg_packet_size"
                ]
            }
        }

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service health status")
    service: str = Field(..., description="Service name")
    version: str = Field(default="1.0.0", description="Service version")
    timestamp: str = Field(..., description="Current timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "service": "feature-extractor",
                "version": "1.0.0",
                "timestamp": "2024-01-15T10:30:45Z"
            }
        }

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "PCAP file not found",
                "error_code": "FILE_NOT_FOUND",
                "details": {
                    "filename": "missing_file.pcap",
                    "path": "/app/pcaps/missing_file.pcap"
                }
            }
        }
