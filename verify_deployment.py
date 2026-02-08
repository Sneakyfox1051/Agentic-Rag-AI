#!/usr/bin/env python3
"""
Verification script to check if everything is ready for Render deployment.
Run this before deploying to ensure all required files and configurations are in place.
"""
import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"[OK] {description}: {filepath}")
        return True
    else:
        print(f"[MISSING] {description}: {filepath}")
        return False

def check_file_content(filepath, required_strings, description):
    """Check if file contains required strings"""
    if not os.path.exists(filepath):
        print(f"✗ File not found: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    all_found = True
    for req_str in required_strings:
        if req_str in content:
            print(f"[OK] {description}: Found '{req_str}' in {filepath}")
        else:
            print(f"[MISSING] {description}: Missing '{req_str}' in {filepath}")
            all_found = False
    
    return all_found

def main():
    print("=" * 60)
    print("Render Deployment Verification")
    print("=" * 60)
    print()
    
    errors = []
    
    # Check required files
    print("Checking required files...")
    print("-" * 60)
    
    required_files = [
        ("render.yaml", "Render configuration"),
        ("requirements.txt", "Python dependencies"),
        ("Procfile", "Process file"),
        ("runtime.txt", "Python runtime version"),
        ("app/main.py", "FastAPI application"),
        ("app/mock_setup.py", "Mock setup"),
        ("frontend/package.json", "Frontend dependencies"),
        ("frontend/src/App.jsx", "React app component"),
        (".gitignore", "Git ignore file"),
    ]
    
    for filepath, description in required_files:
        if not check_file_exists(filepath, description):
            errors.append(f"Missing file: {filepath}")
    
    print()
    
    # Check render.yaml content
    print("Checking render.yaml configuration...")
    print("-" * 60)
    check_file_content("render.yaml", ["buildCommand", "startCommand", "USE_MOCK"], "render.yaml config")
    
    # Check main.py content
    print()
    print("Checking app/main.py configuration...")
    print("-" * 60)
    check_file_content("app/main.py", ["CORSMiddleware", "create_mock_orchestrator", "USE_MOCK"], "main.py config")
    
    # Check requirements.txt
    print()
    print("Checking requirements.txt...")
    print("-" * 60)
    check_file_content("requirements.txt", ["fastapi", "uvicorn", "pydantic"], "Python dependencies")
    
    # Check frontend package.json
    print()
    print("Checking frontend/package.json...")
    print("-" * 60)
    check_file_content("frontend/package.json", ["react", "react-dom", "axios"], "Frontend dependencies")
    
    # Check Procfile
    print()
    print("Checking Procfile...")
    print("-" * 60)
    check_file_content("Procfile", ["$PORT"], "Port configuration")
    
    # Summary
    print()
    print("=" * 60)
    if errors:
        print("[ERROR] DEPLOYMENT NOT READY")
        print(f"Found {len(errors)} issue(s):")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("[SUCCESS] ALL CHECKS PASSED - READY FOR DEPLOYMENT!")
        print()
        print("Next steps:")
        print("1. Push code to GitHub")
        print("2. Connect repository to Render")
        print("3. Deploy using render.yaml")
        sys.exit(0)

if __name__ == "__main__":
    main()
