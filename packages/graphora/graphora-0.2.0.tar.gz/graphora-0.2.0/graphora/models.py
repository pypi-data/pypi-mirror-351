"""
Graphora Models

Data models for the Graphora client library.
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    """Document types supported by Graphora."""
    TXT = "txt"
    PDF = "pdf"
    DOCX = "docx"
    CSV = "csv"
    JSON = "json"
    YAML = "yaml"
    XML = "xml"


class DocumentMetadata(BaseModel):
    """Metadata for a document."""
    source: str
    document_type: DocumentType
    tags: List[str] = Field(default_factory=list)
    custom_metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentInfo(BaseModel):
    """Information about a document."""
    filename: str
    size: int
    document_type: DocumentType
    metadata: Optional[DocumentMetadata] = None


class OntologyResponse(BaseModel):
    """Response from ontology validation."""
    id: str


class TransformationStage(str, Enum):
    """Stages of the transformation process."""
    UPLOAD = "upload"
    PARSING = "parsing"
    EXTRACTION = "extraction"
    VALIDATION = "validation"
    INDEXING = "indexing"
    COMPLETED = "completed"


class ResourceMetrics(BaseModel):
    """Resource usage metrics for a transformation."""
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    duration_seconds: float = 0.0


class StageProgress(BaseModel):
    """Progress information for a transformation stage."""
    stage: TransformationStage
    progress: float = 0.0  # 0.0 to 1.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metrics: Optional[ResourceMetrics] = None
    message: Optional[str] = None


class TransformStatus(BaseModel):
    """Status of a transformation."""
    transform_id: str
    status: str
    progress: float = 0.0  # 0.0 to 1.0
    stage_progress: List[StageProgress] = Field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    resource_metrics: Optional[ResourceMetrics] = None


class TransformResponse(BaseModel):
    """Response from document upload."""
    id: str
    upload_timestamp: datetime
    status: str
    document_info: DocumentInfo


class MergeStatus(BaseModel):
    """Status of a merge process."""
    merge_id: str
    status: str
    progress: float = 0.0  # 0.0 to 1.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error: Optional[str] = None
    conflicts_count: int = 0
    resolved_count: int = 0


class MergeResponse(BaseModel):
    """Response from starting a merge process."""
    merge_id: str
    status: str
    start_time: datetime


class ResolutionStrategy(str, Enum):
    """Strategies for resolving conflicts."""
    ACCEPT = "accept"
    REJECT = "reject"
    MODIFY = "modify"
    MERGE = "merge"


class ConflictResolution(BaseModel):
    """Information about a conflict requiring resolution."""
    id: str
    entity_id: str
    entity_type: str
    properties: Dict[str, Any]
    conflict_type: str
    source: Optional[str] = None
    target: Optional[str] = None
    suggested_resolution: Optional[ResolutionStrategy] = None
    confidence: Optional[float] = None


class Node(BaseModel):
    """A node in the graph."""
    id: str
    labels: List[str]
    properties: Dict[str, Any]


class Edge(BaseModel):
    """An edge in the graph."""
    id: str
    type: str
    source: str
    target: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class GraphResponse(BaseModel):
    """Response containing graph data."""
    nodes: List[Node] = Field(default_factory=list)
    edges: List[Edge] = Field(default_factory=list)
    total_nodes: Optional[int] = None
    total_edges: Optional[int] = None


class NodeChange(BaseModel):
    """A change to a node in the graph."""
    id: Optional[str] = None  # None for new nodes
    labels: List[str]
    properties: Dict[str, Any]
    is_deleted: bool = False


class EdgeChange(BaseModel):
    """A change to an edge in the graph."""
    id: Optional[str] = None  # None for new edges
    type: str
    source: str
    target: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    is_deleted: bool = False


class SaveGraphRequest(BaseModel):
    """Request to save changes to the graph."""
    nodes: List[NodeChange] = Field(default_factory=list)
    edges: List[EdgeChange] = Field(default_factory=list)
    version: Optional[int] = None  # For optimistic concurrency control


class SaveGraphResponse(BaseModel):
    """Response from saving changes to the graph."""
    data: GraphResponse
    messages: Optional[List[str]] = None
