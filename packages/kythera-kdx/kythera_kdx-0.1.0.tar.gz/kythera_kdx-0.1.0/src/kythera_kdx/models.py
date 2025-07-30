"""
Pydantic models for Kythera API requests and responses.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, validator, ConfigDict


class BaseKytheraModel(BaseModel):
    """Base model for all Kythera API models."""
    
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        use_enum_values=True,
        str_strip_whitespace=True
    )


class ErrorResponse(BaseKytheraModel):
    """Standard error response model."""
    
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: Optional[datetime] = Field(None, description="Error timestamp")


class PaginationMeta(BaseKytheraModel):
    """Pagination metadata."""
    
    page: int = Field(..., ge=1, description="Current page number")
    per_page: int = Field(..., ge=1, le=100, description="Items per page")
    total_items: int = Field(..., ge=0, description="Total number of items")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")


class HealthStatus(str, Enum):
    """Health check status values."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthResponse(BaseKytheraModel):
    """Health check response."""
    
    status: HealthStatus = Field(..., description="Service health status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    version: Optional[str] = Field(None, description="API version")
    uptime: Optional[int] = Field(None, description="Service uptime in seconds")
    dependencies: Optional[Dict[str, HealthStatus]] = Field(
        None, description="Status of service dependencies"
    )


class ResourceStatus(str, Enum):
    """Generic resource status values."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    DELETED = "deleted"
    ERROR = "error"


class BaseResource(BaseKytheraModel):
    """Base model for API resources."""
    
    id: str = Field(..., description="Unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    status: ResourceStatus = Field(..., description="Resource status")


class CreateResourceRequest(BaseKytheraModel):
    """Base model for resource creation requests."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Resource name")
    description: Optional[str] = Field(
        None, max_length=1000, description="Resource description"
    )
    tags: Optional[List[str]] = Field(
        None, description="Resource tags"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata"
    )


class UpdateResourceRequest(BaseKytheraModel):
    """Base model for resource update requests."""
    
    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Resource name"
    )
    description: Optional[str] = Field(
        None, max_length=1000, description="Resource description"
    )
    tags: Optional[List[str]] = Field(None, description="Resource tags")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata"
    )
    status: Optional[ResourceStatus] = Field(None, description="Resource status")


class PaginatedResponse(BaseKytheraModel):
    """Generic paginated response."""
    
    data: List[Dict[str, Any]] = Field(..., description="Response data")
    meta: PaginationMeta = Field(..., description="Pagination metadata")


# Example specific models - these would be replaced with actual API models
class User(BaseResource):
    """User model."""
    
    email: str = Field(..., description="User email")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    role: str = Field(..., description="User role")
    is_active: bool = Field(True, description="Whether user is active")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    
    @validator("email")
    def validate_email(cls, v):
        """Validate email format."""
        if "@" not in v:
            raise ValueError("Invalid email format")
        return v.lower()


class CreateUserRequest(CreateResourceRequest):
    """Create user request."""
    
    email: str = Field(..., description="User email")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    role: str = Field("user", description="User role")
    password: Optional[str] = Field(None, description="User password")
    
    @validator("email")
    def validate_email(cls, v):
        """Validate email format."""
        if "@" not in v:
            raise ValueError("Invalid email format")
        return v.lower()


class UpdateUserRequest(UpdateResourceRequest):
    """Update user request."""
    
    email: Optional[str] = Field(None, description="User email")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    role: Optional[str] = Field(None, description="User role")
    is_active: Optional[bool] = Field(None, description="Whether user is active")
    
    @validator("email")
    def validate_email(cls, v):
        """Validate email format."""
        if v and "@" not in v:
            raise ValueError("Invalid email format")
        return v.lower() if v else v


class Project(BaseResource):
    """Project model."""
    
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    owner_id: str = Field(..., description="Project owner ID")
    settings: Optional[Dict[str, Any]] = Field(None, description="Project settings")
    is_public: bool = Field(False, description="Whether project is public")


class CreateProjectRequest(CreateResourceRequest):
    """Create project request."""
    
    is_public: bool = Field(False, description="Whether project is public")
    settings: Optional[Dict[str, Any]] = Field(None, description="Project settings")


class UpdateProjectRequest(UpdateResourceRequest):
    """Update project request."""
    
    is_public: Optional[bool] = Field(None, description="Whether project is public")
    settings: Optional[Dict[str, Any]] = Field(None, description="Project settings")


# Response models
class UserResponse(BaseKytheraModel):
    """Single user response."""
    
    data: User = Field(..., description="User data")


class UsersResponse(PaginatedResponse):
    """Multiple users response."""
    
    data: List[User] = Field(..., description="Users data")


class ProjectResponse(BaseKytheraModel):
    """Single project response."""
    
    data: Project = Field(..., description="Project data")


class ProjectsResponse(PaginatedResponse):
    """Multiple projects response."""
    
    data: List[Project] = Field(..., description="Projects data")


# Query parameter models
class PaginationParams(BaseKytheraModel):
    """Pagination query parameters."""
    
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")


class SortOrder(str, Enum):
    """Sort order values."""
    ASC = "asc"
    DESC = "desc"


class SortParams(BaseKytheraModel):
    """Sort query parameters."""
    
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_order: SortOrder = Field(SortOrder.ASC, description="Sort order")


class FilterParams(BaseKytheraModel):
    """Base filter parameters."""
    
    status: Optional[ResourceStatus] = Field(None, description="Filter by status")
    created_after: Optional[datetime] = Field(None, description="Filter by creation date")
    created_before: Optional[datetime] = Field(None, description="Filter by creation date")
    search: Optional[str] = Field(None, description="Search term")


class UserFilterParams(FilterParams):
    """User-specific filter parameters."""
    
    role: Optional[str] = Field(None, description="Filter by role")
    is_active: Optional[bool] = Field(None, description="Filter by active status")


class ProjectFilterParams(FilterParams):
    """Project-specific filter parameters."""
    
    owner_id: Optional[str] = Field(None, description="Filter by owner")
    is_public: Optional[bool] = Field(None, description="Filter by public status")


# Combined query models
class UserQueryParams(PaginationParams, SortParams, UserFilterParams):
    """Combined user query parameters."""
    pass


class ProjectQueryParams(PaginationParams, SortParams, ProjectFilterParams):
    """Combined project query parameters."""
    pass
