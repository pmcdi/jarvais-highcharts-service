import requests
import pandas as pd
import json
import os

# Define the server URL
SERVER_URL = "http://localhost:5000"

# Path to the sample data
DATA_FILE_PATH = r"C:\Users\samkr\OneDrive\Desktop\code\jarvais\data\RADCURE_Clinical_v04_20241219.csv"

def test_violin_plot():
    """Test the violin plot endpoint with sample data"""
    
    # Check if the data file exists
    if not os.path.exists(DATA_FILE_PATH):
        print(f"Error: Data file not found at {DATA_FILE_PATH}")
        return
    
    # Read the sample data to understand its structure
    try:
        df = pd.read_csv(DATA_FILE_PATH)
        print(f"Data loaded successfully. Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print("First few rows:")
        print(df.head())
        
        # Look for categorical and continuous variables
        categorical_cols = []
        continuous_cols = []
        
        for col in df.columns:
            if df[col].dtype == 'object':
                categorical_cols.append(col)
            elif df[col].dtype in ['int64', 'float64']:
                continuous_cols.append(col)
        
        print(f"\nCategorical columns: {categorical_cols}")
        print(f"Continuous columns: {continuous_cols}")
        
        # Select suitable variables for testing
        if categorical_cols and continuous_cols:
            var_categorical = categorical_cols[1]  # First categorical variable
            var_continuous = continuous_cols[0]    # First continuous variable
            
            print("\nTesting violin plot with:")
            print(f"  Categorical variable: {var_categorical}")
            print(f"  Continuous variable: {var_continuous}")
            
            # Upload the file first
            with open(DATA_FILE_PATH, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{SERVER_URL}/upload", files=files)
                
                if response.status_code in [200, 201]:
                    upload_result = response.json()
                    filename = upload_result.get('filename')
                    analyzer_id = upload_result.get('analyzer_id')
                    print(f"\nFile uploaded successfully: {filename}")
                    
                    # Test the violin plot endpoint
                    violin_data = {
                        'var_categorical': var_categorical,
                        'var_continuous': var_continuous
                    }
                    
                    violin_response = requests.get(f"{SERVER_URL}/visualization/{analyzer_id}/violin_plot", params=violin_data)
                    
                    if violin_response.status_code in [200, 201]:
                        violin_result = violin_response.json()
                        print("\nViolin plot generated successfully!")
                        print(f"Chart title: {violin_result.get('title', {}).get('text', 'N/A')}")
                        print(f"Chart type: {violin_result.get('chart', {}).get('type', 'N/A')}")
                        print(f"Number of series: {len(violin_result.get('series', []))}")
                        
                        # Save the result to a file for inspection
                        with open('violin_plot_result.json', 'w') as f:
                            json.dump(violin_result, f, indent=2)
                        print("\nViolin plot JSON saved to 'violin_plot_result.json'")
                        
                    else:
                        print(f"\n violin plot: {violin_response.status_code}")
                        print(f"Response: {violin_response.text}")
                        
                else:
                    print(f"\nError uploading file: {response.status_code}")
                    print(f"Response: {response.text}")
        else:
            print("Error: Could not find suitable categorical and continuous variables")
            
    except Exception as e:
        print(f"Error reading data file: {e}")

if __name__ == "__main__":
    # First check if server is running
    try:
        response = requests.get(f"{SERVER_URL}/health")
        if response.status_code in [200, 201]:
            print("Server is running. Testing violin plot endpoint...")
            test_violin_plot()
        else:
            print(f"Server health check failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure it's running on port 5000.") 