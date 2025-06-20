import os
import io
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

import pandas as pd
from jarvais import Analyzer
from plot import get_corr_heatmap_json, get_freq_heatmaps_json, get_pie_chart_json, get_umap_json

import redis, pickle, logging


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


# Configuration
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

app.config['REDIS_HOST'] = os.environ.get('REDIS_HOST', 'localhost')
app.config['REDIS_PORT'] = int(os.environ.get('REDIS_PORT', 6379))
app.config['REDIS_DB'] = int(os.environ.get('REDIS_DB', 0))
app.config['SESSION_TTL'] = int(os.environ.get('SESSION_TTL', 3600))  # 1 hour default

ALLOWED_EXTENSIONS = {'csv'}

# Initialize Redis connection
try:
    redis_client = redis.Redis(
        host=app.config['REDIS_HOST'],
        port=app.config['REDIS_PORT'],
        db=app.config['REDIS_DB']
    )
    redis_client.ping()
    USE_REDIS = True
    logger.info("Connected to Redis")
except:
    USE_REDIS = False
    logger.warning("Redis not available, using in-memory storage")
    analyzers: Dict[str, Analyzer] = {}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def check_analyzer(redis_client: redis.Redis, analyzer_id: str) -> bool:
    """
    Checks if a given analyzer_id exists as a key in Redis.

    Args:
        redis_client (redis.Redis): An active Redis client connection instance.
        analyzer_id (str): The ID to check for in Redis.

    Returns:
        bool: True if the key exists, False otherwise.
    """
    try:
        # The .exists() command returns the number of keys that exist from the list provided.
        # For a single key, it returns 1 if it exists, 0 otherwise.
        return redis_client.exists(f"analyzer:{analyzer_id}") == 1
    except redis.exceptions.ConnectionError as e:
        # Handle cases where the Redis server might be down
        print(f"Error connecting to Redis: {e}")
        return False

def store_analyzer(analyzer_id: str, analyzer: Analyzer) -> None:
    """Store analyzer instance in Redis or memory."""
    if USE_REDIS:
        serialized = pickle.dumps(analyzer)
        redis_client.setex(
            f"analyzer:{analyzer_id}",
            app.config['SESSION_TTL'],
            serialized
        )
    else:
        analyzers[analyzer_id] = analyzer

def get_analyzer(analyzer_id: str) -> Optional[Analyzer]:
    """Retrieve analyzer instance from Redis or memory."""
    if USE_REDIS:
        serialized = redis_client.get(f"analyzer:{analyzer_id}")
        if serialized:
            return pickle.loads(serialized)
        return None
    else:
        return analyzers.get(analyzer_id)

def delete_analyzer_storage(analyzer_id: str) -> bool:
    """Delete analyzer instance from storage."""
    if USE_REDIS:
        return redis_client.delete(f"analyzer:{analyzer_id}") > 0
    else:
        if analyzer_id in analyzers:
            del analyzers[analyzer_id]
            return True
        return False

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    return pd.DataFrame(umap_data, columns=['UMAP1', 'UMAP2'], index=data.index)

@app.route('/upload', methods=['POST'])
def upload_csv() -> tuple[Dict[str, Any], int]:
    """
    Upload CSV file and create an Analyzer instance.
    
    Returns:
        JSON response with analyzer_id and basic data info
    """
    print(request.get_json(silent=True))  # Debugging line to print incoming JSON
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in request'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only CSV files are allowed'}), 400
    
    # try:
    # Generate unique ID for this analyzer session
    analyzer_id = str(uuid.uuid4())
    
    # Read CSV directly from memory
    file_content = file.read()
    df = pd.read_csv(io.BytesIO(file_content), index_col=0)
    
    # Initialize Analyzer
    analyzer = Analyzer(df, app.config['UPLOAD_FOLDER'])
    # analyzer.run()

    # Calculate UMAP of continuous variables
    if analyzer.settings.continuous_columns:
        analyzer.umap_data = get_umap(analyzer.data, continuous_columns=analyzer.settings.continuous_columns)
    
    # Store analyzer instance
    store_analyzer(analyzer_id, analyzer)
    
    # Get basic info about the data
    data_info = {
        'analyzer_id': analyzer_id,
        'filename': secure_filename(file.filename),
        'file_shape': df.shape,
        # 'dtypes': df.dtypes.astype(str).to_dict(),
        'categorical_variables': analyzer.settings.categorical_columns,
        'continuous_variables': analyzer.settings.continuous_columns,
        # 'missing_summary': analyzer.missing_summary.to_dict() if hasattr(analyzer, 'missing_summary') else None,
        # 'outlier_summary': analyzer.outlier_summary.to_dict() if hasattr(analyzer, 'outlier_summary') else None,
        'created_at': datetime.now().isoformat(),
        'expires_at': (datetime.utcnow() + timedelta(seconds=app.config['SESSION_TTL'])).isoformat()
    }
    
    
    return jsonify(data_info), 201
        
    # except Exception as e:
    #     return jsonify({'error': f'Failed to process file: {str(e)}'}), 500

@app.route('/visualization/<analyzer_id>/correlation_heatmap', methods=['GET'])
def get_correlation_heatmap(analyzer_id: str) -> tuple[Dict[str, Any], int]:
    """
    Get correlation heatmap for continuous variables.
    
    Args:
        analyzer_id: Unique identifier for the analyzer instance
        method: Method to use for generating the heatmap (e.g., 'pearson', 'spearman')
        
    Returns:
        JSON response with base64 encoded image or error
    """
    if not check_analyzer(redis_client, analyzer_id):
        return jsonify({'error': 'Analyzer not found'}), 404
    
    try:
        method = request.args.get('method')
        analyzer = get_analyzer(analyzer_id)

        # Generate correlation heatmap
        chart_json = get_corr_heatmap_json(analyzer.data[analyzer.settings.continuous_columns], method=method)
        return jsonify(chart_json), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to generate correlation heatmap: {str(e)}'}), 500

@app.route('/visualization/<analyzer_id>/frequency_heatmap', methods=['GET'])
def get_frequency_heatmap(analyzer_id: str) -> tuple[Dict[str, Any], int]:
    """
    Get frequency heatmap for categorical variables.
    
    Args:
        analyzer_id: Unique identifier for the analyzer instance
        
    Returns:
        JSON response with base64 encoded image or error
    """
    if not check_analyzer(redis_client, analyzer_id):
        return jsonify({'error': 'Analyzer not found'}), 404
    
    # try:
    analyzer = get_analyzer(analyzer_id)
    column1 = request.args.get('column1')
    column2 = request.args.get('column2')

    print(column1, column2)
    print(analyzer.settings.categorical_columns)
    
    if column1 not in analyzer.settings.categorical_columns or column2 not in analyzer.settings.categorical_columns:
        return jsonify({'error': 'Invalid or missing categorical columns'}), 400

    # Generate frequency heatmap
    chart_json = get_freq_heatmaps_json(analyzer.data, column1, column2)
    return jsonify(chart_json), 200

    # except Exception as e:
    #     print(e)
    #     return jsonify({'error': f'Failed to generate frequency heatmap: {str(e)}'}), 500

@app.route('/visualization/<analyzer_id>/pie_chart', methods=['GET'])
def get_pie_chart(analyzer_id: str) -> tuple[Dict[str, Any], int]:
    """
    Get pie chart for a specific variable.
    
    Args:
        analyzer_id: Unique identifier for the analyzer instance
        var: The variable to plot

    Returns:
        JSON response with base64 encoded image or error
    """
    if not check_analyzer(redis_client, analyzer_id):
        return jsonify({'error': 'Analyzer not found'}), 404

    var = request.args.get('var')
    if not var:
        return jsonify({'error': 'Variable not specified'}), 400

    # try:
    analyzer = get_analyzer(analyzer_id)
    chart_json = get_pie_chart_json(analyzer.data, var)
    return jsonify(chart_json), 200

    # except Exception as e:
    #     return jsonify({'error': f'Failed to generate pie chart: {str(e)}'}), 500

@app.route('/visualization/<analyzer_id>/umap_scatterplot', methods=['GET'])
def get_umap_plot(analyzer_id: str) -> tuple[Dict[str, Any], int]:
    """
    [ WARNING: This endpoint is current broken.]

    Get pie chart for a specific variable.
    
    Args:
        analyzer_id: Unique identifier for the analyzer instance
        var: The variable to plot

    Returns:
        JSON response with base64 encoded image or error
    """
    return jsonify({'error': 'This endpoint is currently broken.'}), 500

    if not check_analyzer(redis_client, analyzer_id):
        return jsonify({'error': 'Analyzer not found'}), 404
    
    analyzer = get_analyzer(analyzer_id)
    
    hue = request.args.get('hue')
    if hue:
        hue_data = analyzer.data[hue] if hue in analyzer.data.columns else None
    else:
        hue_data = None

    chart_json = get_umap_json(analyzer.umap_data, hue_data)
    return jsonify(chart_json), 200

    # except Exception as e:
    #     return jsonify({'error': f'Failed to generate pie chart: {str(e)}'}), 500

@app.route('/analyzers', methods=['GET'])
def list_analyzers() -> tuple[Dict[str, Any], int]:
    """List all active analyzer sessions."""
    if USE_REDIS:
        # Get all keys matching the analyzer pattern
        keys = redis_client.keys("analyzer:*")
        analyzers = {key.decode('utf-8').split(':')[1]: True for key in keys}
        
        analyzer_list = [
            {
                'analyzer_id': aid,
                'has_data': True
            } for aid in analyzers.keys()
        ]
        
        return jsonify({
            'count': len(analyzer_list),
            'analyzers': analyzer_list
        }), 200
        
    else:
        analyzer_list = [
            {
                'analyzer_id': aid,
                'has_data': aid in analyzers
            }
            for aid in analyzers.keys()
        ]
        
        return jsonify({
            'count': len(analyzer_list),
            'analyzers': analyzer_list
        }), 200

@app.route('/analyzers/<analyzer_id>', methods=['GET'])
def analyzer_info(analyzer_id: str) -> tuple[Dict[str, Any], int]:
    """Get information about a specific analyzer."""
    if not check_analyzer(redis_client, analyzer_id):
        return jsonify({'error': 'Analyzer not found'}), 404

    try:
        analyzer = get_analyzer(analyzer_id)
        data_info = {
                'analyzer_id': analyzer_id,
                'file_shape': analyzer.data.shape,
                'categorical_variables': analyzer.settings.categorical_columns,
                'continuous_variables': analyzer.settings.continuous_columns,
            }
        
        return jsonify(data_info), 200
    except Exception as e:
        return jsonify({'error': f'Failed to generate pie chart: {str(e)}'}), 500

@app.route('/api/v1/analyzers/<analyzer_id>', methods=['DELETE'])
def delete_analyzer(analyzer_id: str) -> tuple[Dict[str, Any], int]:
    """Delete an analyzer session."""
    if delete_analyzer_storage(analyzer_id):
        logger.info(f"Deleted analyzer {analyzer_id}")
        return jsonify({'message': f'Analyzer {analyzer_id} deleted successfully'}), 200
    else:
        return jsonify({'error': 'Analyzer not found'}), 404

@app.route('/api/v1/health', methods=['GET'])
def health_check() -> tuple[Dict[str, Any], int]:
    """Health check endpoint."""
    health_status = {
        'status': 'healthy',
        'storage': 'redis' if USE_REDIS else 'memory',
        'timestamp': datetime.utcnow().isoformat()
    }

    if USE_REDIS:
        try:
            redis_client.ping()
            health_status['redis'] = 'connected'
        except:
            health_status['status'] = 'degraded'
            health_status['redis'] = 'disconnected'
    
    return jsonify(health_status), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)