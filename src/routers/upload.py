import io
import uuid
import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, File, UploadFile, HTTPException, Request
import pandas as pd

from jarvais import Analyzer
from ..config import settings
from ..storage import storage_manager
from ..models import AnalyzerInfo

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["upload"])

# Rate limiting setup (only for production)
if settings.production:
    from slowapi import Limiter
    from slowapi.util import get_remote_address
    
    limiter = Limiter(key_func=get_remote_address)
else:
    limiter = None


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in settings.allowed_extensions


def drop_uid_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drop columns with number of unique values equal to the number of rows.
    """
    uid_columns = [col for col in df.columns if df[col].nunique() == df.shape[0]]
    print(f"Dropping columns of unique values: {uid_columns}")
    return df.drop(columns=uid_columns)


def get_umap(data: pd.DataFrame, continuous_columns: list) -> pd.DataFrame:
    """
    Generate UMAP projection for continuous variables.
    
    Args:
        data (pd.DataFrame): Input DataFrame containing the data.
        continuous_columns (list): List of continuous variable column names.
        
    Returns:
        pd.DataFrame: UMAP transformed data.
    """
    from umap import UMAP
    umap_data = UMAP(n_components=2, random_state=42).fit_transform(data[continuous_columns])
    return pd.DataFrame(umap_data, columns=pd.Index(['UMAP1', 'UMAP2']), index=data.index)


@router.post("", response_model=AnalyzerInfo, status_code=201)
@limiter.limit(settings.rate_limit_upload) if limiter else lambda f: f
async def upload_csv(request: Request, file: UploadFile = File(...)):
    """
    Upload CSV file and create an Analyzer instance.
    
    Args:
        request: FastAPI request object (required for rate limiting)
        file: CSV file to upload
        
    Returns:
        AnalyzerInfo: Information about the created analyzer
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected")
    
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    # Read file content
    file_content = await file.read()
    
    # Check file size (production only)
    if settings.production and len(file_content) > settings.max_content_length:
        raise HTTPException(status_code=413, detail="File too large")
    
    try:
        # Generate unique ID for this analyzer session
        analyzer_id = str(uuid.uuid4())
        
        # Read CSV directly from memory
        df = pd.read_csv(io.BytesIO(file_content), index_col=0)
        df = drop_uid_columns(df)
        
        # Initialize Analyzer
        analyzer = Analyzer(df, settings.upload_folder)
        
        # Calculate UMAP of continuous variables
        if analyzer.settings.continuous_columns:
            # Ugly hack to get UMAP data into the analyzer. It allows UMAP to be saved in Redis.
            analyzer.umap_data = get_umap(analyzer.data, continuous_columns=analyzer.settings.continuous_columns) # type: ignore
        
        # Store analyzer instance
        storage_manager.store_analyzer(analyzer_id, analyzer)
        
        # Return basic info about the data
        return AnalyzerInfo(
            analyzer_id=analyzer_id,
            filename=file.filename,
            file_shape=df.shape,
            categorical_variables=analyzer.settings.categorical_columns,
            continuous_variables=analyzer.settings.continuous_columns,
            created_at=datetime.now().isoformat(),
            expires_at=(datetime.now(timezone.utc) + timedelta(seconds=settings.session_ttl)).isoformat()
        )
        
    except Exception as e:
        logger.error(f"Failed to process file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}") 