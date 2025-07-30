"""
Video-related operations for the NomadicML SDK.
"""

import time
import os
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
import requests
from datetime import datetime

from .client import NomadicML
from .types import VideoSource, ProcessingStatus, Severity, EventType
from .utils import (
    validate_api_key, validate_file_path, validate_url,
    validate_youtube_url, get_file_mime_type, get_filename_from_path
)
from .exceptions import VideoUploadError, AnalysisError, NomadicMLError, ValidationError

logger = logging.getLogger("nomadicml")


class VideoClient:
    """
    Client for video upload and analysis operations.
    
    This class extends the base NomadicML client with video-specific operations.
    
    Args:
        client: An initialized NomadicML client.
    """
    
    def __init__(self, client: NomadicML):
        """
        Initialize the video client with a NomadicML client.
        
        Args:
            client: An initialized NomadicML client.
        """
        self.client = client
        self._user_info = None
        
    async def _get_auth_user(self) -> Optional[Dict[str, Any]]:
        """
        Get the authenticated user information.
        
        Returns:
            A dictionary with user information if available, None otherwise.
        """
        if self.user_info:
            return self.user_info
            
        try:
            response = self.client._make_request(
                method="POST",
                endpoint="/api/keys/verify",
            )
            
            self.user_info = response.json()
            return self.user_info
        except Exception as e:
            logger.warning(f"Failed to get authenticated user info: {e}")
            return None
    
    def get_user_id(self) -> Optional[str]:
        """
        Get the authenticated user ID.
        
        Returns:
            The user ID if available, None otherwise.
        """
        # Try to get cached user info
        if self._user_info and "user_id" in self._user_info:
            return self._user_info["user_id"]
        
        # Make a synchronous request to get user info
        try:
            response = self.client._make_request(
                method="POST",
                endpoint="/api/keys/verify"
            )
            self._user_info = response.json()
            return self._user_info.get("user_id")
        except Exception as e:
            logger.warning(f"Failed to get user ID: {str(e)}")
            return None
    
    def upload_video(
        self,
        source: Union[str, VideoSource],
        file_path: Optional[str] = None,
        youtube_url: Optional[str] = None,
        video_id: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Upload a video for analysis.
        
        Args:
            source: The source of the video. Can be "file", "youtube", or "saved".
            file_path: Path to the video file (required when source is "file").
            youtube_url: YouTube URL (required when source is "youtube").
            video_id: Existing video ID (required when source is "saved").
            created_by: User identifier for tracking. If not provided, the authenticated user ID will be used.
            
        Returns:
            A dictionary with the upload status and video_id.
            
        Raises:
            ValidationError: If the input parameters are invalid.
            VideoUploadError: If the upload fails.
            APIError: If the API returns an error.
            NomadicMLError: For any other errors.
        """
        # Convert string source to enum if needed
        if isinstance(source, str):
            try:
                source = VideoSource(source)
            except ValueError:
                raise ValueError(f"Invalid source: {source}. Must be one of {[s.value for s in VideoSource]}")
        
        # Validate inputs based on source
        if source == VideoSource.FILE and not file_path:
            raise ValidationError("file_path is required when source is 'file'")
        elif source == VideoSource.YOUTUBE and not youtube_url:
            raise ValidationError("youtube_url is required when source is 'youtube'")
        elif source == VideoSource.SAVED and not video_id:
            raise ValidationError("video_id is required when source is 'saved'")
        
        # Validate file path if provided
        if source == VideoSource.FILE and file_path:
            validate_file_path(file_path)
        
        # Validate YouTube URL if provided
        if source == VideoSource.YOUTUBE and youtube_url:
            validate_youtube_url(youtube_url)
        
        # Use authenticated user ID if created_by is not provided
        if not created_by:
            user_id = self.get_user_id()
            created_by = user_id if user_id else "api_client"
        
        # Prepare request data
        endpoint = "/api/upload-video"
        
        # Prepare form data
        form_data = {
            "source": source.value,
            "firebase_collection_name": self.client.collection_name,
            "created_by": created_by,
        }
        
        # Add file or YouTube URL based on source
        files = None
        if source == VideoSource.FILE:
            filename = get_filename_from_path(file_path)
            mime_type = get_file_mime_type(file_path)
            
            # Open the file for upload
            with open(file_path, "rb") as f:
                file_content = f.read()
            
            # Create a multipart/form-data request
            files = {"file": (filename, file_content, mime_type)}
        elif source == VideoSource.YOUTUBE:
            form_data["youtube_url"] = youtube_url
        elif source == VideoSource.SAVED:
            form_data["video_id"] = video_id
        
        # Make the request
        response = self.client._make_request(
            method="POST",
            endpoint=endpoint,
            data=form_data,
            files=files,
            timeout=120,  # Longer timeout for uploads
        )
        
        # Return the parsed JSON response
        return response.json()
    
    def analyze_video(self, video_id: str, created_by: Optional[str] = None) -> Dict[str, Any]:
        """
        Start analysis for an uploaded video.
        
        Args:
            video_id: The ID of the video to analyze.
            created_by: User identifier for tracking. If not provided, the authenticated user ID will be used.
            
        Returns:
            A dictionary with the analysis status.
            
        Raises:
            AnalysisError: If the analysis fails to start.
            APIError: If the API returns an error.
            NomadicMLError: For any other errors.
        """
        endpoint = f"/api/analyze-video/{video_id}"
        
        # Use authenticated user ID if created_by is not provided
        if not created_by:
            user_id = self.get_user_id()
            created_by = user_id if user_id else "api_client"
        
        # Prepare form data with the collection name
        data = {
            "firebase_collection_name": self.client.collection_name,
            "created_by": created_by,
        }
        
        # Make the request
        response = self.client._make_request(
            method="POST",
            endpoint=endpoint,
            data=data,
        )
        
        # Return the parsed JSON response
        return response.json()
    
    def get_video_status(self, video_id: str) -> Dict[str, Any]:
        """
        Get the status of a video analysis.
        
        Args:
            video_id: The ID of the video.
            
        Returns:
            A dictionary with the video status.
            
        Raises:
            APIError: If the API returns an error.
            NomadicMLError: For any other errors.
        """
        endpoint = f"/api/video/{video_id}/status"
        
        # Add the required collection_name parameter
        params = {"firebase_collection_name": self.client.collection_name}
        
        # Make the request
        response = self.client._make_request("GET", endpoint, params=params)
        
        # Return the parsed JSON response
        return response.json()

    def wait_for_analysis(
        self,
        video_id: str,
        timeout: int = 600,  # 10 minutes
        poll_interval: int = 5,  # 5 seconds
    ) -> Dict[str, Any]:
        """
        Wait for a video analysis to complete.
        
        Args:
            video_id: The ID of the video.
            timeout: Maximum time to wait in seconds.
            poll_interval: Time between status checks in seconds.
            
        Returns:
            The final video status.
            
        Raises:
            TimeoutError: If the analysis does not complete within the timeout.
            APIError: If the API returns an error.
            NomadicMLError: For any other errors.
        """
        start_time = time.time()
        consecutive_errors = 0
        max_consecutive_errors = 3
        
        while time.time() - start_time < timeout:
            try:
                status = self.get_video_status(video_id)
                # Log the full response for debugging
                logger.debug(f"Raw status response: {status}")
                
                # Extract the status value from the nested structure safely
                current_status = None
                
                # Handle different response structures
                if isinstance(status, dict):
                    # If status is directly in the root object
                    if "status" in status and isinstance(status["status"], str):
                        current_status = status["status"]
                    # If status is in a nested status object
                    elif "status" in status and isinstance(status["status"], dict) and "status" in status["status"]:
                        current_status = status["status"]["status"]
                    # If status is in visual_analysis
                    elif "metadata" in status and isinstance(status["metadata"], dict) and "visual_analysis" in status["metadata"]:
                        visual_analysis = status["metadata"]["visual_analysis"]
                        if "status" in visual_analysis:
                            if isinstance(visual_analysis["status"], str):
                                current_status = visual_analysis["status"]
                            elif isinstance(visual_analysis["status"], dict) and "status" in visual_analysis["status"]:
                                current_status = visual_analysis["status"]["status"]
                
                # Normalize status value
                if current_status:
                    logger.info(f"Video analysis status: {current_status}")
                    
                    # Check if analysis is completed
                    if current_status.upper() in ["COMPLETED", "COMPLETE"]:
                        return status
                    
                    # Check if analysis failed
                    if current_status.upper() in ["FAILED", "ERROR"]:
                        error_msg = "Unknown error"
                        if "error" in status:
                            error_msg = status.get("error", "Unknown error")
                        elif isinstance(status.get("status"), dict) and "message" in status["status"]:
                            error_msg = status["status"]["message"]
                        
                        raise AnalysisError(f"Video analysis failed: {error_msg}")
                
                # Get progress if available
                progress = None
                if isinstance(status.get("status"), dict) and "progress" in status["status"]:
                    progress = status["status"]["progress"]
                elif "downloadProgress" in status and isinstance(status["downloadProgress"], dict):
                    progress = status["downloadProgress"].get("percentage", 0)
                
                if progress:
                    logger.info(f"Analysis progress: {progress}%")
                
                consecutive_errors = 0  # Reset error counter on success
                
                # Wait before checking again
                if poll_interval > 0:  # Skip sleep in tests
                    time.sleep(poll_interval)
                
            except Exception as e:
                consecutive_errors += 1
                logger.warning(f"Error checking analysis status (attempt {consecutive_errors}): {str(e)}")
                
                if consecutive_errors >= max_consecutive_errors:
                    raise NomadicMLError(f"Error waiting for completion: {str(e)}")
                
                # Exponential backoff
                backoff_time = min(30, poll_interval * (2 ** (consecutive_errors - 1)))
                if backoff_time > 0:  # Skip sleep in tests
                    time.sleep(backoff_time)
        
        # If we get here, the timeout was reached
        raise TimeoutError(f"Timed out waiting for video analysis to complete after {timeout} seconds")


    def get_video_events(
        self,
        video_id: str,
        severity: Optional[Union[str, Severity]] = None,
        event_type: Optional[Union[str, EventType]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get events detected in a video.
        
        Args:
            video_id: The ID of the video.
            severity: Filter events by severity.
            event_type: Filter events by type.
            
        Returns:
            A list of detected events.
            
        Raises:
            APIError: If the API returns an error.
            NomadicMLError: For any other errors.
        """
        endpoint = f"/api/video/{video_id}/events"
        
        # Prepare query parameters
        params = {}
        
        if severity:
            if isinstance(severity, str):
                severity = Severity(severity)
            params["severity"] = severity.value
            
        if event_type:
            if isinstance(event_type, str):
                event_type = EventType(event_type)
            params["event_type"] = event_type.value
            
        response = self.client._make_request(
            method="GET",
            endpoint=endpoint,
            params=params,
        )
        
        return response.json()
    
    def get_video_analysis(self, video_id: str) -> Dict[str, Any]:
        """
        Get the complete analysis of a video.
        
        Args:
            video_id: The ID of the video.
            
        Returns:
            The complete video analysis.
            
        Raises:
            APIError: If the API returns an error.
            NomadicMLError: For any other errors.
        """
        endpoint = f"/api/video/{video_id}/analysis"
        params = {"firebase_collection_name": self.client.collection_name}
                
        response = self.client._make_request(
            method="GET",
            endpoint=endpoint,
            params=params,
        )
        
        return response.json()
    
    def upload_and_analyze(
        self,
        file_path: str,
        wait_for_completion: bool = True,
        timeout: int = 600,  # 10 minutes
        created_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Upload a video file and start analysis in one operation.
        
        Args:
            file_path: Path to the video file.
            wait_for_completion: Whether to wait for analysis to complete.
            timeout: Maximum time to wait for analysis in seconds.
            created_by: User identifier for tracking. If not provided, the authenticated user ID will be used.
            
        Returns:
            The video analysis result or status.
            
        Raises:
            ValidationError: If the input parameters are invalid.
            VideoUploadError: If the upload fails.
            AnalysisError: If the analysis fails.
            TimeoutError: If the analysis does not complete within the timeout.
            APIError: If the API returns an error.
            NomadicMLError: For any other errors.
        """
        # Validate file path - directly call here to allow mocking in tests
        validate_file_path(file_path)
        
        # Upload the video
        upload_result = self.upload_video(
            source=VideoSource.FILE,
            file_path=file_path,
            created_by=created_by,
        )
        
        video_id = upload_result.get("video_id")
        if not video_id:
            raise NomadicMLError("Failed to get video ID from upload response")
        
        # Start analysis
        analysis_result = self.analyze_video(
            video_id=video_id,
            created_by=created_by,
        )
        
        # Wait for analysis to complete if requested
        if wait_for_completion:
            final_status = self.wait_for_analysis(
                video_id=video_id,
                timeout=timeout,
            )
            
            # Get the full analysis
            analysis = self.get_video_analysis(video_id)
            return analysis
        
        return analysis_result
