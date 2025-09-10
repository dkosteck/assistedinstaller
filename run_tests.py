#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test runner script for assistedinstaller collection

This script provides an easy way to run tests with various options.

assisted-by: Claude 3.5 Sonnet (Cursor)
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / 'plugins' / 'modules'))
sys.path.insert(0, str(current_dir / 'plugins' / 'module_utils'))


def run_command(cmd, description="Running command"):
    """Run a command and return the result"""
    print(f"\n{description}...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Success!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Failed!")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {cmd[0]}")
        return False


def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    try:
        import pytest
        print(f"✅ pytest {pytest.__version__}")
    except ImportError:
        print("❌ pytest not installed. Run: pip install -r tests/unit/requirements.txt")
        return False
    
    try:
        import requests
        print(f"✅ requests {requests.__version__}")
    except ImportError:
        print("❌ requests not installed. Run: pip install -r tests/unit/requirements.txt")
        return False
    
    return True


def validate_modules():
    """Validate that all modules can be imported"""
    print("\n🔍 Validating module imports...")
    
    modules_dir = current_dir / 'plugins' / 'modules'
    if not modules_dir.exists():
        print("❌ Modules directory not found")
        return False
    
    success = True
    for module_file in modules_dir.glob('*.py'):
        if module_file.name.startswith('__'):
            continue
        
        module_name = module_file.stem
        try:
            __import__(module_name)
            print(f"✅ {module_name}")
        except Exception as e:
            print(f"❌ {module_name}: {e}")
            success = False
    
    return success


def main():
    parser = argparse.ArgumentParser(description='Test runner for assistedinstaller collection')
    parser.add_argument('--coverage', action='store_true', help='Run tests with coverage')
    parser.add_argument('--module', help='Run tests for specific module')
    parser.add_argument('--file', help='Run specific test file')
    parser.add_argument('--smoke', action='store_true', help='Run smoke tests only')
    parser.add_argument('--validate', action='store_true', help='Validate module imports only')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--no-deps-check', action='store_true', help='Skip dependency check')
    
    args = parser.parse_args()
    
    print("🚀 assistedinstaller Test Runner")
    print("=" * 40)
    
    # Check dependencies unless skipped
    if not args.no_deps_check and not check_dependencies():
        print("\n❌ Dependency check failed. Install requirements first:")
        print("   pip install -r tests/unit/requirements.txt")
        sys.exit(1)
    
    # Validate modules if requested
    if args.validate:
        if validate_modules():
            print("\n✅ All modules validated successfully!")
            sys.exit(0)
        else:
            print("\n❌ Module validation failed!")
            sys.exit(1)
    
    # Build pytest command
    cmd = ['python', '-m', 'pytest']
    
    if args.verbose:
        cmd.append('-v')
    
    if args.coverage:
        cmd.extend(['--cov=plugins/modules', '--cov-report=term-missing', '--cov-report=html'])
    
    if args.smoke:
        cmd.extend(['-k', 'test_missing_requests_library or test_api_authentication_headers'])
        cmd.append('--tb=short')
    elif args.module:
        cmd.append(f'tests/unit/test_{args.module}.py')
    elif args.file:
        cmd.append(f'tests/unit/{args.file}')
    else:
        cmd.append('tests/unit/')
    
    # Run the tests
    success = run_command(cmd, "Running tests")
    
    if success:
        print("\n🎉 All tests passed!")
        if args.coverage:
            print("\n📊 Coverage report generated:")
            print("   - Terminal: see above")
            print("   - HTML: open htmlcov/index.html")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()
