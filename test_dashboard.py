#!/usr/bin/env python3
"""
Test script for the dashboard endpoint
"""
import requests
import json
import sys

def test_dashboard():
    # Base URL - adjust if using different port
    BASE_URL = "http://localhost:8888"
    
    # Test data CSV
    test_data = """index,age,sex,bmi,children,smoker,region
0,19,female,27.9,0,yes,southwest
1,18,male,33.77,1,no,southeast
2,28,male,33.0,3,no,southeast
3,33,male,22.705,0,no,northwest
4,32,male,28.88,0,no,northwest
5,31,female,25.74,0,no,southeast
6,46,female,33.44,1,no,southeast
7,37,female,27.74,3,no,northwest
8,37,male,29.83,2,no,northeast
9,60,female,25.84,0,no,northwest
10,25,male,26.22,0,no,northeast
11,62,female,26.29,0,yes,southeast
12,23,male,34.4,0,no,southwest
13,56,female,39.82,0,no,southeast
14,27,male,42.13,0,yes,southeast
15,19,male,24.6,1,no,southwest
16,52,female,30.78,1,no,northeast
17,23,male,23.845,0,no,northeast
18,56,male,40.3,0,no,southwest
19,30,male,35.3,0,yes,southwest
20,60,female,36.005,0,no,northeast
21,30,female,32.4,1,no,southwest
22,18,male,34.1,0,no,southeast
23,34,female,31.92,1,yes,northeast
24,37,male,28.025,2,no,northwest
25,59,female,27.72,3,no,southeast
26,63,female,23.085,0,no,northeast
27,55,female,32.775,2,no,northwest
28,23,male,17.385,1,no,northwest
29,31,male,36.3,2,yes,southwest"""
    
    # Save test data to file
    with open('test_dashboard_data.csv', 'w') as f:
        f.write(test_data)
    
    print(f"Testing dashboard endpoint at {BASE_URL}")
    print("=" * 50)
    
    # Step 1: Upload CSV
    print("\n1. Uploading CSV file...")
    with open('test_dashboard_data.csv', 'rb') as f:
        files = {'file': ('test_dashboard_data.csv', f, 'text/csv')}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    
    if response.status_code != 201:
        print(f"❌ Upload failed: {response.status_code}")
        print(response.text)
        return False
    
    upload_result = response.json()
    analyzer_id = upload_result['analyzer_id']
    print(f"✅ Upload successful. Analyzer ID: {analyzer_id}")
    print(f"   Shape: {upload_result['file_shape']}")
    print(f"   Categorical vars: {upload_result['categorical_variables']}")
    print(f"   Continuous vars: {upload_result['continuous_variables']}")
    
    # Step 2: Get dashboard
    print(f"\n2. Getting dashboard for analyzer {analyzer_id}...")
    response = requests.get(f"{BASE_URL}/dashboard/{analyzer_id}")
    
    if response.status_code != 200:
        print(f"❌ Dashboard request failed: {response.status_code}")
        print(response.text)
        return False
    
    dashboard_data = response.json()
    
    # Check if it's a list of charts
    if isinstance(dashboard_data, list):
        print(f"✅ Dashboard generated successfully with {len(dashboard_data)} charts")
        print(dashboard_data)
        # Analyze the charts
        chart_types = {}
        for i, chart in enumerate(dashboard_data):
            if '_metadata' in chart:
                chart_type = chart['_metadata'].get('type', 'unknown')
                chart_types[chart_type] = chart_types.get(chart_type, 0) + 1
                
                # Print details for significant plots
                if chart_type in ['box_plot', 'violin_plot']:
                    cat_var = chart['_metadata'].get('categorical_var', 'N/A')
                    cont_var = chart['_metadata'].get('continuous_var', 'N/A')
                    p_value = chart['_metadata'].get('p_value', 'N/A')
                    significant = chart['_metadata'].get('significant', False)
                    
                    sig_marker = "⭐" if significant else ""
                    print(f"   Chart {i+1}: {chart_type} - {cont_var} by {cat_var} (p={p_value:.4f if isinstance(p_value, float) else p_value}) {sig_marker}")
                elif chart_type == 'umap_scatterplot':
                    hue_var = chart['_metadata'].get('hue_variable', 'None')
                    print(f"   Chart {i+1}: UMAP colored by {hue_var}")
        
        print(f"\nChart type summary:")
        for chart_type, count in chart_types.items():
            print(f"   {chart_type}: {count}")
    else:
        print(f"⚠️  Unexpected dashboard format (expected list, got {type(dashboard_data)})")
        print(json.dumps(dashboard_data, indent=2)[:500])
    
    print("\n✅ Dashboard endpoint test completed successfully!")
    return True

if __name__ == "__main__":
    success = test_dashboard()
    sys.exit(0 if success else 1)
