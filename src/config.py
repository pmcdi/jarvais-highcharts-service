import os
from typing import Set, List
from pydantic import BaseModel


class Settings(BaseModel):
    """Application settings with environment-based configuration."""
    
    # Application settings
    title: str = "Jarvais Highcharts Service"
    description: str = "A FastAPI service for data analysis and visualization using Jarvais"
    version: str = "1.0.0"
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8888
    log_level: str = "info"
    
    # Production mode toggle
    production: bool = False
    
    # File upload settings
    max_content_length: int = 100 * 1024 * 1024  # 100MB
    upload_folder: str = "uploads"
    allowed_extensions: Set[str] = {"csv"}
    
    # Redis settings
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    session_ttl: int = 3600  # 1 hour
    
    # Security settings
    allowed_origins: List[str] = ["*"]
    trusted_hosts: List[str] = []
    
    # Rate limiting settings (for production)
    rate_limit_upload: str = "10/minute"
    rate_limit_visualization: str = "30/minute"
    rate_limit_general: str = "60/minute"
    
    def __init__(self, **kwargs):
        # Load from environment variables
        env_values = {
            'production': os.environ.get('PRODUCTION', 'false').lower() == 'true',
            'host': os.environ.get('HOST', '0.0.0.0'),
            'port': int(os.environ.get('PORT', 8888)),
            'log_level': os.environ.get('LOG_LEVEL', 'info'),
            'max_content_length': int(os.environ.get('MAX_CONTENT_LENGTH', 100 * 1024 * 1024)),
            'upload_folder': os.environ.get('UPLOAD_FOLDER', 'uploads'),
            'redis_host': os.environ.get('REDIS_HOST', 'redis'),
            'redis_port': int(os.environ.get('REDIS_PORT', 6379)),
            'redis_db': int(os.environ.get('REDIS_DB', 0)),
            'session_ttl': int(os.environ.get('SESSION_TTL', 3600)),
            'allowed_origins': os.environ.get('ALLOWED_ORIGINS', '*').split(','),
            'trusted_hosts': os.environ.get('TRUSTED_HOSTS', '').split(',') if os.environ.get('TRUSTED_HOSTS') else [],
            'rate_limit_upload': os.environ.get('RATE_LIMIT_UPLOAD', '10/minute'),
            'rate_limit_visualization': os.environ.get('RATE_LIMIT_VISUALIZATION', '30/minute'),
            'rate_limit_general': os.environ.get('RATE_LIMIT_GENERAL', '60/minute'),
        }
        
        # Merge with provided kwargs
        env_values.update(kwargs)
        super().__init__(**env_values)
    
    class Config:
        # Allow arbitrary types for complex settings
        arbitrary_types_allowed = True


# Global settings instance
settings = Settings() 