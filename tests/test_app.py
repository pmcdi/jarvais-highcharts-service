import pytest
import json
import uuid
from unittest.mock import patch, MagicMock
from werkzeug.datastructures import FileStorage


class TestHealthCheck:
    """Test health check endpoint."""
    
    def test_health_check_success(self, client):
        """Test successful health check."""
        response = client.get('/api/v1/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'status' in data
        assert 'timestamp' in data
        assert 'storage' in data

    @patch('src.app_production.redis_client')
    def test_health_check_redis_down(self, mock_redis, client):
        """Test health check when Redis is down."""
        mock_redis.ping.side_effect = Exception("Redis connection failed")
        
        response = client.get('/api/v1/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        if 'redis' in data:
            assert data['status'] == 'degraded'
            assert data['redis'] == 'disconnected'


class TestFileUpload:
    """Test file upload functionality."""
    
    def test_upload_valid_csv(self, client, sample_csv_file):
        """Test uploading a valid CSV file."""
        response = client.post('/upload', data={
            'file': (sample_csv_file, 'test.csv')
        }, content_type='multipart/form-data')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        
        assert 'analyzer_id' in data
        assert 'filename' in data
        assert 'file_shape' in data
        assert 'categorical_variables' in data
        assert 'continuous_variables' in data
        assert 'created_at' in data
        assert 'expires_at' in data
        
        # Validate UUID format
        assert uuid.UUID(data['analyzer_id'])
    
    def test_upload_no_file(self, client):
        """Test upload without file."""
        response = client.post('/upload', data={})
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'No file part' in data['error']
    
    def test_upload_empty_filename(self, client):
        """Test upload with empty filename."""
        response = client.post('/upload', data={
            'file': (b'', '')
        }, content_type='multipart/form-data')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'No file selected' in data['error']
    
    def test_upload_invalid_extension(self, client):
        """Test upload with invalid file extension."""
        response = client.post('/upload', data={
            'file': (b'some content', 'test.txt')
        }, content_type='multipart/form-data')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Only CSV files are allowed' in data['error']


class TestVisualizationEndpoints:
    """Test visualization endpoints."""
    
    def test_correlation_heatmap_invalid_id(self, client):
        """Test correlation heatmap with invalid analyzer ID."""
        response = client.get('/visualization/invalid-id/correlation_heatmap')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Invalid analyzer ID format' in data['error']
    
    def test_correlation_heatmap_not_found(self, client, sample_analyzer_id):
        """Test correlation heatmap with non-existent analyzer."""
        response = client.get(f'/visualization/{sample_analyzer_id}/correlation_heatmap')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Analyzer not found' in data['error']
    
    def test_frequency_heatmap_invalid_id(self, client):
        """Test frequency heatmap with invalid analyzer ID."""
        response = client.get('/visualization/invalid-id/frequency_heatmap')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_pie_chart_invalid_id(self, client):
        """Test pie chart with invalid analyzer ID."""
        response = client.get('/visualization/invalid-id/pie_chart')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_pie_chart_missing_var(self, client, sample_analyzer_id):
        """Test pie chart without variable parameter."""
        response = client.get(f'/visualization/{sample_analyzer_id}/pie_chart')
        assert response.status_code == 404  # Will fail on analyzer not found first


class TestAnalyzerManagement:
    """Test analyzer management endpoints."""
    
    def test_list_analyzers(self, client):
        """Test listing analyzers."""
        response = client.get('/analyzers')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'count' in data
        assert 'analyzers' in data
        assert isinstance(data['analyzers'], list)
    
    def test_analyzer_info_not_found(self, client, sample_analyzer_id):
        """Test getting info for non-existent analyzer."""
        response = client.get(f'/analyzers/{sample_analyzer_id}')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Analyzer not found' in data['error']
    
    def test_delete_analyzer_not_found(self, client, sample_analyzer_id):
        """Test deleting non-existent analyzer."""
        response = client.delete(f'/api/v1/analyzers/{sample_analyzer_id}')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Analyzer not found' in data['error']


class TestSecurity:
    """Test security features."""
    
    def test_security_headers(self, client):
        """Test that security headers are present."""
        response = client.get('/api/v1/health')
        
        assert 'X-Content-Type-Options' in response.headers
        assert response.headers['X-Content-Type-Options'] == 'nosniff'
        assert 'X-Frame-Options' in response.headers
        assert response.headers['X-Frame-Options'] == 'DENY'
        assert 'X-XSS-Protection' in response.headers
        assert response.headers['X-XSS-Protection'] == '1; mode=block'


class TestInputValidation:
    """Test input validation."""
    
    def test_validate_analyzer_id_valid(self):
        """Test validation of valid UUID."""
        from src.app_production import validate_analyzer_id
        
        valid_uuid = str(uuid.uuid4())
        assert validate_analyzer_id(valid_uuid) is True
    
    def test_validate_analyzer_id_invalid(self):
        """Test validation of invalid UUID."""
        from src.app_production import validate_analyzer_id
        
        assert validate_analyzer_id('invalid-uuid') is False
        assert validate_analyzer_id('123') is False
        assert validate_analyzer_id('') is False


@pytest.mark.integration
class TestIntegration:
    """Integration tests requiring full functionality."""
    
    @patch('src.app_production.USE_REDIS', False)
    def test_upload_and_visualize_memory_backend(self, client, sample_csv_file):
        """Test complete workflow with memory backend."""
        # Upload file
        upload_response = client.post('/upload', data={
            'file': (sample_csv_file, 'test.csv')
        }, content_type='multipart/form-data')
        
        assert upload_response.status_code == 201
        upload_data = json.loads(upload_response.data)
        analyzer_id = upload_data['analyzer_id']
        
        # Test analyzer info
        info_response = client.get(f'/analyzers/{analyzer_id}')
        assert info_response.status_code == 200
        
        info_data = json.loads(info_response.data)
        assert 'file_shape' in info_data
        assert 'categorical_variables' in info_data
        assert 'continuous_variables' in info_data
        
        # Test deletion
        delete_response = client.delete(f'/api/v1/analyzers/{analyzer_id}')
        assert delete_response.status_code == 200
        
        # Verify deletion
        info_response_after = client.get(f'/analyzers/{analyzer_id}')
        assert info_response_after.status_code == 404
