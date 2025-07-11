from typing import Optional, List
from pydantic import BaseModel, Field


class AnalyzerInfo(BaseModel):
    analyzer_id: str = Field(..., description="Unique identifier for the analyzer")
    filename: Optional[str] = Field(None, description="Original filename")
    file_shape: tuple = Field(..., description="Shape of the uploaded data")
    categorical_variables: List[str] = Field(..., description="List of categorical variables")
    continuous_variables: List[str] = Field(..., description="List of continuous variables")
    created_at: str = Field(..., description="Creation timestamp")
    expires_at: Optional[str] = Field(None, description="Expiration timestamp")


class AnalyzerListItem(BaseModel):
    analyzer_id: str = Field(..., description="Unique identifier for the analyzer")
    has_data: bool = Field(..., description="Whether the analyzer has data")


class AnalyzerList(BaseModel):
    count: int = Field(..., description="Number of analyzers")
    analyzers: List[AnalyzerListItem] = Field(..., description="List of analyzers")


class HealthStatus(BaseModel):
    status: str = Field(..., description="Service status")
    storage: str = Field(..., description="Storage type being used")
    timestamp: str = Field(..., description="Current timestamp")
    redis: Optional[str] = Field(None, description="Redis connection status")
    version: str = Field(..., description="API version")
    mode: str = Field(..., description="Application mode")


class SuccessResponse(BaseModel):
    message: str = Field(..., description="Success message")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details") 