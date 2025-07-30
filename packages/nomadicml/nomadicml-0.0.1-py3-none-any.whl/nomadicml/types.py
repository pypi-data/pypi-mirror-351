"""Type definitions for the NomadicML SDK."""

from enum import Enum
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from datetime import datetime


class VideoSource(str, Enum):
    """Video source types."""
    
    FILE = "file"
    YOUTUBE = "youtube"
    SAVED = "saved"


class ProcessingStatus(str, Enum):
    """Video processing status types."""
    
    UPLOADING = "uploading"
    UPLOADING_FAILED = "uploading_failed"
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class EventType(str, Enum):
    """Event types detected in videos."""
    
    DMV_COMPLIANCE = "DMV Compliance"
    SAFETY_ALERT = "Safety Alert"
    DRIVE_QUALITY = "Drive Quality"
    TRAFFIC_VIOLATION = "Traffic Violation"
    NEAR_COLLISION = "Near Collision"


class Severity(str, Enum):
    """Severity levels for detected events."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Event:
    """Represents a detected event in a video."""
    
    time: float
    type: EventType
    severity: Severity
    description: str
    dmv_rule: str
    metrics: Dict[str, Any]
    ai_analysis: Optional[str] = None
    recommendations: Optional[str] = None


@dataclass
class VideoMetadata:
    """Metadata information about a video."""
    
    duration: float
    frame_count: int
    fps: float
    width: int
    height: int
    original_url: Optional[str] = None
    title: Optional[str] = None


@dataclass
class VideoAnalysis:
    """Complete analysis of a video."""
    
    video_id: str
    status: ProcessingStatus
    filename: str
    upload_time: datetime
    metadata: Optional[VideoMetadata] = None
    events: List[Dict[str, Any]] = None
    analysis: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
