from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import pandas as pd
import io
import base64
from typing import Dict, Any, Optional
import os
import uuid
from datetime import datetime
from jarvais import Analyzer
from .plot import get_corr_heatmap_json, get_freq_heatmaps_json, get_pie_chart_json
app = Flask(__name__)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

# In-memory storage for analyzers (in production, use Redis or similar)
analyzers: Dict[str, Analyzer] = {}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['POST'])
def upload_csv() -> tuple[Dict[str, Any], int]:
    """
    Upload CSV file and create an Analyzer instance.
    
    Returns:
        JSON response with analyzer_id and basic data info
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in request'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only CSV files are allowed'}), 400
    
    try:
        # Generate unique ID for this analyzer session
        analyzer_id = str(uuid.uuid4())
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{analyzer_id}_{filename}")
        file.save(filepath)
        
        # Read CSV and initialize Analyzer
        df = pd.read_csv(filepath)
        analyzer = Analyzer(df)
        
        # Store analyzer instance
        analyzers[analyzer_id] = analyzer
        
        # Get basic info about the data
        data_info = {
            'analyzer_id': analyzer_id,
            'file_shape': df.shape,
            'categorical_variables': analyzer.categorical_variables,
            'continuous_variables': analyzer.continuous_variables,
            'missing_summary': analyzer.missing_summary.to_dict() if hasattr(analyzer, 'missing_summary') else None,
            'outlier_summary': analyzer.outlier_summary.to_dict() if hasattr(analyzer, 'outlier_summary') else None,
            'created_at': datetime.now().isoformat()
        }
        
        # Clean up temporary file
        os.remove(filepath)
        
        return jsonify(data_info), 201
        
    except Exception as e:
        return jsonify({'error': f'Failed to process file: {str(e)}'}), 500

@app.route('/visualization/<analyzer_id>/correlation_heatmap/<method>', methods=['GET'])
def get_correlation_heatmap(analyzer_id: str, method: str) -> tuple[Dict[str, Any], int]:
    """
    Get correlation heatmap for continuous variables.
    
    Args:
        analyzer_id: Unique identifier for the analyzer instance
        method: Method to use for generating the heatmap (e.g., 'pearson', 'spearman')
        
    Returns:
        JSON response with base64 encoded image or error
    """
    if analyzer_id not in analyzers:
        return jsonify({'error': 'Analyzer not found'}), 404
    
    try:
        analyzer = analyzers[analyzer_id]
        
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
    if analyzer_id not in analyzers:
        return jsonify({'error': 'Analyzer not found'}), 404
    
    try:
        analyzer = analyzers[analyzer_id]
        
        # Generate frequency heatmap
        chart_json = get_freq_heatmaps_json(analyzer.data[analyzer.settings.categorical_columns])
        return jsonify(chart_json), 200

    except Exception as e:
        return jsonify({'error': f'Failed to generate frequency heatmap: {str(e)}'}), 500


@app.route('/visualization/<analyzer_id>/pairplot', methods=['GET'])
def get_pairplot(analyzer_id: str) -> tuple[Dict[str, Any], int]:
    """
    Get pairplot for continuous variables.
    
    Args:
        analyzer_id: Unique identifier for the analyzer instance
        
    Returns:
        JSON response with base64 encoded image or error
    """
    if analyzer_id not in analyzers:
        return jsonify({'error': 'Analyzer not found'}), 404
    
    try:
        analyzer = analyzers[analyzer_id]
        
        # Get optional parameters
        max_vars = request.args.get('max_vars', default=10, type=int)
        
        # Generate pairplot
        fig = analyzer.pairplot(max_vars=max_vars)
        
        # Convert matplotlib figure to base64
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        
        return jsonify({
            'analyzer_id': analyzer_id,
            'visualization_type': 'pairplot',
            'image': img_base64,
            'format': 'png',
            'parameters': {'max_vars': max_vars}
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to generate pairplot: {str(e)}'}), 500


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
    if analyzer_id not in analyzers:
        return jsonify({'error': 'Analyzer not found'}), 404

    var = request.args.get('var')
    if not var:
        return jsonify({'error': 'Variable not specified'}), 400

    try:
        analyzer = analyzers[analyzer_id]
        chart_json = get_pie_chart_json(analyzer.data, var)
        return jsonify(chart_json), 200

    except Exception as e:
        return jsonify({'error': f'Failed to generate pie chart: {str(e)}'}), 500

@app.route('/analyzers', methods=['GET'])
def list_analyzers() -> tuple[Dict[str, Any], int]:
    """List all active analyzer sessions."""
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

@app.route('/analyzers/<analyzer_id>', methods=['DELETE'])
def delete_analyzer(analyzer_id: str) -> tuple[Dict[str, Any], int]:
    """Delete an analyzer session."""
    if analyzer_id not in analyzers:
        return jsonify({'error': 'Analyzer not found'}), 404

    del analyzers[analyzer_id]
    return jsonify({'message': f'Analyzer {analyzer_id} deleted successfully'}), 200

@app.route('/health', methods=['GET'])
def health_check() -> tuple[Dict[str, Any], int]:
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'active_analyzers': len(analyzers)
    }), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)