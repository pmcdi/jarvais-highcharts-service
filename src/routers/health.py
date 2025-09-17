from datetime import datetime

from fastapi import APIRouter, Request

from ..config import settings
from ..storage import storage_manager
from ..models import HealthStatus
from ..utils.rate_limit import apply_rate_limit

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthStatus)
@apply_rate_limit(settings.rate_limit_general)
async def health_check(request: Request):
    """Health check endpoint."""
    storage_health = storage_manager.health_check()
    
    health_status = HealthStatus(
        status=storage_health.get('status', 'healthy'),
        storage=storage_health.get('storage_type', 'unknown'),
        timestamp=datetime.utcnow().isoformat(),
        redis=storage_health.get('redis', None),
        version=settings.version,
        mode="production" if settings.production else "development"
    )
    
    return health_status 