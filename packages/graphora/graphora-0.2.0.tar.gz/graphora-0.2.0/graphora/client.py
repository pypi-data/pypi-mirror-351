"""
Graphora Client

Main client class for interacting with the Graphora API.
"""

import os
import requests
import json
import time
from typing import Dict, List, Optional, Union, BinaryIO, Any
from pathlib import Path

from graphora.models import (
    OntologyResponse,
    TransformResponse,
    TransformStatus,
    MergeResponse,
    MergeStatus,
    GraphResponse,
    DocumentMetadata,
    ConflictResolution,
    ResolutionStrategy,
    SaveGraphRequest,
    SaveGraphResponse
)
from graphora.exceptions import GraphoraAPIError, GraphoraClientError


class GraphoraClient:
    """
    Client for interacting with the Graphora API.
    
    This client provides methods for all major Graphora API endpoints, including:
    - Ontology management
    - Document transformation
    - Graph merging
    - Graph querying and manipulation
    """
    
    def __init__(
        self,
        base_url: str,
        user_id: str,
        api_key: Optional[str] = None,
        timeout: int = 60
    ):
        """
        Initialize a new Graphora client.
        
        Args:
            base_url: Base URL of the Graphora API (e.g., "https://api.graphora.example.com")
            user_id: User's ID (required for all API calls)
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.user_id = user_id
        self.api_key = api_key or os.environ.get("GRAPHORA_API_KEY")
        self.timeout = timeout
        self.api_version = "v1"
        
    @property
    def headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        headers = {
            "Accept": "application/json",
            "user-id": self.user_id  # Add user-id header to all requests
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    def _build_url(self, endpoint: str) -> str:
        """Build a full URL for the given endpoint."""
        if endpoint.startswith("/"):
            endpoint = endpoint[1:]
        return f"{self.base_url}/api/{self.api_version}/{endpoint}"
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and raise appropriate exceptions."""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_msg = str(e)
            try:
                error_data = response.json()
                if "detail" in error_data:
                    error_msg = error_data["detail"]
            except (ValueError, json.JSONDecodeError):
                pass
            raise GraphoraAPIError(f"API error: {error_msg}", response.status_code)
        except (ValueError, json.JSONDecodeError):
            raise GraphoraClientError("Invalid JSON response from API")
        except requests.exceptions.RequestException as e:
            raise GraphoraClientError(f"Request failed: {str(e)}")
    
    # Ontology Endpoints
    
    def register_ontology(self, ontology_yaml: str) -> OntologyResponse:
        """
        Register, validate and upload an ontology definition.
        
        Args:
            ontology_yaml: Ontology definition in YAML format
            
        Returns:
            OntologyResponse with the ID of the validated ontology
        """
        url = self._build_url("ontology")
        data = {"text": ontology_yaml}
        response = requests.post(url, json=data, headers=self.headers, timeout=self.timeout)
        result = self._handle_response(response)
        return OntologyResponse(**result)
    
    def get_ontology(self, ontology_id: str) -> str:
        """
        Retrieve an ontology by ID.
        
        Args:
            ontology_id: ID of the ontology to retrieve
            
        Returns:
            Ontology YAML text
        """
        url = self._build_url(f"ontology/{ontology_id}")
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        result = self._handle_response(response)
        return result.get("text", "")
    
    # Transform Endpoints
    
    def transform(
        self,
        ontology_id: str,
        files: List[Union[str, Path, BinaryIO]],
        metadata: Optional[List[DocumentMetadata]] = None
    ) -> TransformResponse:
        """
        Upload documents for processing.
        
        Args:
            ontology_id: ID of the ontology to use for transformation
            files: List of files to process (paths or file-like objects)
            metadata: Optional metadata for each document
            
        Returns:
            TransformResponse with the ID for tracking progress
        """
        url = self._build_url(f"transform/{ontology_id}/upload")
        
        # Prepare files for upload
        upload_files = []
        for i, file in enumerate(files):
            if isinstance(file, (str, Path)):
                path = Path(file)
                filename = path.name
                file_obj = open(path, "rb")
            else:
                # Assume file-like object
                filename = getattr(file, "name", f"file_{i}")
                file_obj = file
                
            upload_files.append(("files", (filename, file_obj)))
        
        response = requests.post(
            url,
            files=upload_files,
            headers=self.headers,
            timeout=self.timeout
        )
        
        # Close file objects if we opened them
        for _, (_, file_obj) in upload_files:
            if isinstance(files[_], (str, Path)):
                file_obj.close()
        
        result = self._handle_response(response)
        return TransformResponse(**result)
    
    def get_transform_status(
        self,
        transform_id: str,
        include_metrics: bool = True
    ) -> TransformStatus:
        """
        Get the status of a transformation.
        
        Args:
            transform_id: ID of the transformation to check
            include_metrics: Whether to include resource metrics
            
        Returns:
            TransformStatus with current progress
        """
        url = self._build_url(f"transform/status/{transform_id}")
        params = {"include_metrics": include_metrics}
        response = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
        result = self._handle_response(response)
        return TransformStatus(**result)
    
    def wait_for_transform(
        self,
        transform_id: str,
        timeout: int = 300,
        poll_interval: int = 5
    ) -> TransformStatus:
        """
        Wait for a transformation to complete.
        
        Args:
            transform_id: ID of the transformation to wait for
            timeout: Maximum time to wait in seconds
            poll_interval: Time between status checks in seconds
            
        Returns:
            Final TransformStatus
            
        Raises:
            GraphoraClientError: If the transformation fails or times out
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = self.get_transform_status(transform_id)
            if status.status in ["COMPLETED", "FAILED"]:
                return status
            time.sleep(poll_interval)
        
        raise GraphoraClientError(f"Transform {transform_id} timed out after {timeout} seconds")
    
    def cleanup_transform(self, transform_id: str) -> bool:
        """
        Clean up transformation data.
        
        Args:
            transform_id: ID of the transformation to clean up
            
        Returns:
            True if cleanup was successful
        """
        url = self._build_url(f"transform/cleanup/{transform_id}")
        response = requests.delete(url, headers=self.headers, timeout=self.timeout)
        result = self._handle_response(response)
        return result.get("success", False)
    
    def get_transformed_graph(
        self,
        transform_id: str,
        limit: int = 1000,
        skip: int = 0
    ) -> GraphResponse:
        """
        Retrieve graph data by transform ID.
        
        Args:
            transform_id: ID of the transformation
            limit: Maximum number of nodes to return
            skip: Number of nodes to skip for pagination
            
        Returns:
            GraphResponse with nodes and edges
        """
        url = self._build_url(f"graph/{transform_id}")
        params = {"limit": limit, "skip": skip}
        response = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
        result = self._handle_response(response)
        return GraphResponse(**result)
    
    def update_transform_graph(
        self,
        transform_id: str,
        changes: SaveGraphRequest
    ) -> SaveGraphResponse:
        """
        Save bulk modifications to the graph.
        
        Args:
            transform_id: ID of the transformation
            changes: Batch of modifications to apply
            
        Returns:
            SaveGraphResponse with updated graph data
        """
        url = self._build_url(f"graph/{transform_id}")
        response = requests.put(url, json=changes.dict(), headers=self.headers, timeout=self.timeout)
        result = self._handle_response(response)
        return SaveGraphResponse(**result)
    
    # Merge Endpoints
    
    def start_merge(
        self,
        session_id: str,
        transform_id: str,
        merge_id: Optional[str] = None
    ) -> MergeResponse:
        """
        Start a new merge process.
        
        Args:
            session_id: Session ID (ontology ID)
            transform_id: ID of the transformation to merge
            merge_id: Optional custom merge ID
            
        Returns:
            MergeResponse with the ID for tracking progress
        """
        url = self._build_url(f"merge/{session_id}/{transform_id}/start")
        params = {}
        if merge_id:
            params["merge_id"] = merge_id
            
        response = requests.post(url, params=params, headers=self.headers, timeout=self.timeout)
        result = self._handle_response(response)
        return MergeResponse(**result)
    
    def get_merge_status(self, merge_id: str) -> MergeStatus:
        """
        Get the status of a merge process.
        
        Args:
            merge_id: ID of the merge to check
            
        Returns:
            MergeStatus with current progress
        """
        url = self._build_url(f"merge/{merge_id}/status")
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        result = self._handle_response(response)
        return MergeStatus(**result)
    
    def get_conflicts(self, merge_id: str) -> List[ConflictResolution]:
        """
        Get conflicts for a merge process.
        
        Args:
            merge_id: ID of the merge process
            
        Returns:
            List of conflicts requiring resolution
        """
        url = self._build_url(f"merge/{merge_id}/conflicts")
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        result = self._handle_response(response)
        return [ConflictResolution(**item) for item in result]
    
    def resolve_conflict(
        self,
        merge_id: str,
        conflict_id: str,
        changed_props: Dict[str, Any],
        resolution: ResolutionStrategy,
        learning_comment: str = ""
    ) -> bool:
        """
        Apply a resolution to a specific conflict.
        
        Args:
            merge_id: ID of the merge process
            conflict_id: ID of the conflict to resolve
            changed_props: Properties that were changed
            resolution: The resolution decision
            learning_comment: Comment on the resolution
            
        Returns:
            True if the resolution was applied successfully
        """
        url = self._build_url(f"merge/{merge_id}/conflicts/{conflict_id}/resolve")
        data = {
            "changed_props": changed_props,
            "resolution": resolution,
            "learning_comment": learning_comment
        }
        response = requests.post(url, json=data, headers=self.headers, timeout=self.timeout)
        result = self._handle_response(response)
        return result
    
    def get_merge_statistics(self, merge_id: str) -> Dict[str, Any]:
        """
        Get detailed statistics of a merge operation.
        
        Args:
            merge_id: ID of the merge process
            
        Returns:
            Dictionary of merge statistics
        """
        url = self._build_url(f"merge/statistics/{merge_id}")
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        return self._handle_response(response)
    
    def get_merged_graph(self, merge_id: str, transform_id: str) -> GraphResponse:
        """
        Retrieve graph data for a merge process.
        
        Args:
            merge_id: ID of the merge process
            transform_id: ID of the transformation
            
        Returns:
            GraphResponse with nodes and edges
        """
        url = self._build_url(f"merge/graph/{merge_id}/{transform_id}")
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        result = self._handle_response(response)
        return GraphResponse(**result)
