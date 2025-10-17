import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, Path, Request

from ..storage import storage_manager
from ..models import AnalyzerInfo, AnalyzerList, AnalyzerListItem, SuccessResponse
from ..config import settings
from ..utils.rate_limit import apply_rate_limit

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analyzers", tags=["analyzers"])


@router.get("", response_model=AnalyzerList)
@apply_rate_limit(settings.rate_limit_general)
async def list_analyzers(request: Request):
    """List all active analyzer sessions."""
    analyzer_ids = storage_manager.list_analyzer_ids()
    
    analyzer_list = [
        AnalyzerListItem(analyzer_id=aid, has_data=True)
        for aid in analyzer_ids
    ]
    
    return AnalyzerList(count=len(analyzer_list), analyzers=analyzer_list)


@router.get("/{analyzer_id}", response_model=AnalyzerInfo)
@apply_rate_limit(settings.rate_limit_general)
async def analyzer_info(
    request: Request,
    analyzer_id: str = Path(..., description="Unique identifier for the analyzer instance")
):
    """Get information about a specific analyzer."""
    if not storage_manager.check_analyzer(analyzer_id):
        raise HTTPException(status_code=404, detail="Analyzer not found")

    try:
        analyzer = storage_manager.get_analyzer(analyzer_id)
        if not analyzer:
            raise HTTPException(status_code=404, detail="Analyzer not found")
        
        data_info = AnalyzerInfo(
            analyzer_id=analyzer_id,
            filename=None,  # We don't store filename, so use None
            file_shape=analyzer.input_data.shape,
            categorical_variables=analyzer.settings.categorical_columns,
            continuous_variables=analyzer.settings.continuous_columns,
            created_at=datetime.now().isoformat(),  # Note: we don't store creation time, so using current time
            expires_at=None  # We don't store expiration time, so use None
        )
        
        return data_info
    except Exception as e:
        logger.error(f"Failed to get analyzer info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get analyzer info: {str(e)}")


@router.delete("/{analyzer_id}", response_model=SuccessResponse)
async def delete_analyzer(
    analyzer_id: str = Path(..., description="Unique identifier for the analyzer instance")
):
    """Delete an analyzer session."""
    if storage_manager.delete_analyzer(analyzer_id):
        logger.info(f"Deleted analyzer {analyzer_id}")
        return SuccessResponse(message=f"Analyzer {analyzer_id} deleted successfully")
    else:
        raise HTTPException(status_code=404, detail="Analyzer not found") 