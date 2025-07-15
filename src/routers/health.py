from datetime import datetime

from fastapi import APIRouter, Request

from ..config import settings
from ..storage import storage_manager
from ..models import HealthStatus

router = APIRouter(prefix="/health", tags=["health"])

# Rate limiting setup (only for production)
if settings.production:
    from slowapi import Limiter
    from slowapi.util import get_remote_address
    
    limiter = Limiter(key_func=get_remote_address)
else:
    limiter = None


@router.get("", response_model=HealthStatus)
@limiter.limit(settings.rate_limit_general) if limiter else lambda f: f
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