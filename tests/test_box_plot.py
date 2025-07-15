import requests
import pandas as pd
import json
import os

# Define the server URL
SERVER_URL = "http://localhost:5000"

# Path to the sample data
DATA_FILE_PATH = r"C:\Users\samkr\OneDrive\Desktop\code\jarvais\data\RADCURE_Clinical_v04_20241219.csv"

def test_box_plot_endpoints():
    """Test the box plot endpoints with sample data"""
    
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
        if len(categorical_cols) >= 2 and continuous_cols:
            var_categorical = categorical_cols[1]  # First categorical variable (skip patient_id)
            var_grouping = categorical_cols[2] if len(categorical_cols) > 2 else categorical_cols[0]  # Another categorical for grouping
            var_continuous = continuous_cols[0]    # First continuous variable
            
            print("\nTesting box plot with:")
            print(f"  Categorical variable: {var_categorical}")
            print(f"  Continuous variable: {var_continuous}")
            print(f"  Grouping variable: {var_grouping}")
            
            # Upload the file first
            with open(DATA_FILE_PATH, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{SERVER_URL}/upload", files=files)
                
                if response.status_code in [200, 201]:
                    upload_result = response.json()
                    filename = upload_result.get('filename')
                    analyzer_id = upload_result.get('analyzer_id')
                    print(f"\nFile uploaded successfully: {filename}")
                    print(f"Analyzer ID: {analyzer_id}")
                    
                    # Test 1: Standard box plot endpoint
                    print("\n" + "="*50)
                    print("Testing Standard Box Plot Endpoint")
                    print("="*50)
                    
                    box_data = {
                        'var_categorical': var_categorical,
                        'var_continuous': var_continuous
                    }
                    
                    box_response = requests.get(f"{SERVER_URL}/visualization/{analyzer_id}/box_plot", params=box_data)
                    
                    if box_response.status_code in [200, 201]:
                        box_result = box_response.json()
                        print("✅ Standard box plot generated successfully!")
                        print(f"Chart title: {box_result.get('title', {}).get('text', 'N/A')}")
                        print(f"Chart type: {box_result.get('chart', {}).get('type', 'N/A')}")
                        print(f"Number of series: {len(box_result.get('series', []))}")
                        
                        # Check for outliers
                        outlier_series = [s for s in box_result.get('series', []) if s.get('name') == 'Outliers']
                        if outlier_series:
                            print(f"Outliers detected: {len(outlier_series[0].get('data', []))} outliers")
                        else:
                            print("No outliers detected")
                        
                        # Save the result to a file for inspection
                        with open('box_plot_result.json', 'w') as f:
                            json.dump(box_result, f, indent=2)
                        print("Box plot JSON saved to 'box_plot_result.json'")
                        
                    else:
                        print(f"❌ Error creating standard box plot: {box_response.status_code}")
                        print(f"Response: {box_response.text}")
                    
                    # Test 2: Grouped box plot endpoint
                    print("\n" + "="*50)
                    print("Testing Grouped Box Plot Endpoint")
                    print("="*50)
                    
                    grouped_box_data = {
                        'var_categorical': var_categorical,
                        'var_continuous': var_continuous,
                        'var_grouping': var_grouping
                    }
                    
                    grouped_box_response = requests.get(f"{SERVER_URL}/visualization/{analyzer_id}/grouped_box_plot", params=grouped_box_data)
                    
                    if grouped_box_response.status_code in [200, 201]:
                        grouped_box_result = grouped_box_response.json()
                        print("✅ Grouped box plot generated successfully!")
                        print(f"Chart title: {grouped_box_result.get('title', {}).get('text', 'N/A')}")
                        print(f"Chart type: {grouped_box_result.get('chart', {}).get('type', 'N/A')}")
                        print(f"Number of series: {len(grouped_box_result.get('series', []))}")
                        
                        # Check for different groups
                        boxplot_series = [s for s in grouped_box_result.get('series', []) if s.get('type') == 'boxplot']
                        outlier_series = [s for s in grouped_box_result.get('series', []) if s.get('type') == 'scatter']
                        
                        print(f"Number of boxplot series (groups): {len(boxplot_series)}")
                        print(f"Number of outlier series: {len(outlier_series)}")
                        
                        if boxplot_series:
                            print("Groups found:")
                            for series in boxplot_series:
                                print(f"  - {series.get('name', 'Unknown')}")
                        
                        # Save the result to a file for inspection
                        with open('grouped_box_plot_result.json', 'w') as f:
                            json.dump(grouped_box_result, f, indent=2)
                        print("Grouped box plot JSON saved to 'grouped_box_plot_result.json'")
                        
                    else:
                        print(f"❌ Error creating grouped box plot: {grouped_box_response.status_code}")
                        print(f"Response: {grouped_box_response.text}")
                    
                    # Test 3: Error handling - Invalid variables
                    print("\n" + "="*50)
                    print("Testing Error Handling")
                    print("="*50)
                    
                    invalid_data = {
                        'var_categorical': 'invalid_column',
                        'var_continuous': var_continuous
                    }
                    
                    error_response = requests.get(f"{SERVER_URL}/visualization/{analyzer_id}/box_plot", params=invalid_data)
                    
                    if error_response.status_code == 400:
                        print("✅ Error handling working correctly - invalid categorical variable rejected")
                    else:
                        print(f"❌ Unexpected response for invalid variable: {error_response.status_code}")
                        
                else:
                    print(f"\nError uploading file: {response.status_code}")
                    print(f"Response: {response.text}")
        else:
            print("Error: Could not find suitable categorical and continuous variables")
            
    except Exception as e:
        print(f"Error reading data file: {e}")


def test_comparison_with_violin_plot():
    """Compare box plot with violin plot using the same data"""
    
    # Check if the data file exists
    if not os.path.exists(DATA_FILE_PATH):
        print(f"Error: Data file not found at {DATA_FILE_PATH}")
        return
    
    try:
        df = pd.read_csv(DATA_FILE_PATH)
        
        # Get variable info
        categorical_cols = [col for col in df.columns if df[col].dtype == 'object']
        continuous_cols = [col for col in df.columns if df[col].dtype in ['int64', 'float64']]
        
        if len(categorical_cols) >= 1 and continuous_cols:
            var_categorical = categorical_cols[1]  # Skip patient_id
            var_continuous = continuous_cols[0]
            
            print("\nComparing Box Plot vs Violin Plot:")
            print(f"  Variables: {var_continuous} by {var_categorical}")
            
            # Upload the file
            with open(DATA_FILE_PATH, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{SERVER_URL}/upload", files=files)
                
                if response.status_code in [200, 201]:
                    upload_result = response.json()
                    analyzer_id = upload_result.get('analyzer_id')
                    
                    # Get both plots
                    plot_data = {
                        'var_categorical': var_categorical,
                        'var_continuous': var_continuous
                    }
                    
                    # Box plot
                    box_response = requests.get(f"{SERVER_URL}/visualization/{analyzer_id}/box_plot", params=plot_data)
                    
                    # Violin plot
                    violin_response = requests.get(f"{SERVER_URL}/visualization/{analyzer_id}/violin_plot", params=plot_data)
                    
                    if box_response.status_code in [200, 201] and violin_response.status_code in [200, 201]:
                        box_result = box_response.json()
                        violin_result = violin_response.json()
                        
                        print("\n📊 Box Plot:")
                        print(f"   Title: {box_result.get('title', {}).get('text', 'N/A')}")
                        print(f"   Series: {len(box_result.get('series', []))}")
                        
                        print("\n🎻 Violin Plot:")
                        print(f"   Title: {violin_result.get('title', {}).get('text', 'N/A')}")
                        print(f"   Series: {len(violin_result.get('series', []))}")
                        
                        # Save comparison results
                        comparison_result = {
                            "box_plot": box_result,
                            "violin_plot": violin_result
                        }
                        
                        with open('box_vs_violin_comparison.json', 'w') as f:
                            json.dump(comparison_result, f, indent=2)
                        print("\n📁 Comparison results saved to 'box_vs_violin_comparison.json'")
                        
                    else:
                        print("❌ Error generating comparison plots")
                        
    except Exception as e:
        print(f"Error in comparison test: {e}")


if __name__ == "__main__":
    # First check if server is running
    try:
        response = requests.get(f"{SERVER_URL}/health")
        if response.status_code in [200, 201]:
            print("✅ Server is running. Testing box plot endpoints...")
            print("\n" + "="*60)
            print("BOX PLOT ENDPOINT TESTING")
            print("="*60)
            
            test_box_plot_endpoints()
            
            print("\n" + "="*60)
            print("COMPARISON TESTING")
            print("="*60)
            
            test_comparison_with_violin_plot()
            
            print("\n" + "="*60)
            print("TESTING COMPLETED")
            print("="*60)
            
        else:
            print(f"❌ Server health check failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the server. Make sure it's running on port 5000.")
    except Exception as e:
        print(f"❌ Error: {e}") 