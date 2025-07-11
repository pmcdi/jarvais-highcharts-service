#!/usr/bin/env python3
"""
Startup script for the FastAPI Jarvais Highcharts Service
"""

import uvicorn
import os

def main():
    """Run the FastAPI application"""
    
    # Determine which app to run
    app_file = os.environ.get('APP_FILE', 'main')
    app_name = os.environ.get('APP_NAME', 'app')
    
    # Get configuration from environment
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    reload = os.environ.get('RELOAD', 'false').lower() == 'true'
    log_level = os.environ.get('LOG_LEVEL', 'info')
    
    # Remove .py extension if present
    if app_file.endswith('.py'):
        app_file = app_file[:-3]
    
    # Construct the app module path
    app_module = f"src.{app_file}:{app_name}"
    
    print("Starting FastAPI application...")
    print(f"App module: {app_module}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Reload: {reload}")
    print(f"Log level: {log_level}")
    print()
    
    # Run the application
    uvicorn.run(
        app_module,
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
        access_log=True
    )

if __name__ == "__main__":
    main() 