#!/usr/bin/env python3
"""
Verify the new project structure is working correctly.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all critical imports work."""
    print("Testing imports...")
    
    tests = [
        ("Backend Models", "from backend.models.state_encoding import StateEncoder"),
        ("Backend API", "from backend.api.dependencies import initialize_pgm_service"),
        ("Backend Services", "from backend.services.cache_service import get_cache_service"),
        ("Backend Pipelines", "from backend.pipelines.batch_pipeline import BatchPipeline"),
        ("Data Ingestion", "from data.ingestion.ingestion import DataIngestion"),
        ("Data Validation", "from data.validation.validator import DataValidator"),
        ("Data Features", "from data.features.offline_store import OfflineFeatureStore"),
        ("Utils", "from utils.logger import get_logger"),
        ("Config", "from config import config"),
    ]
    
    passed = 0
    failed = 0
    
    for name, import_stmt in tests:
        try:
            exec(import_stmt)
            print(f"  ✅ {name}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {name}: {e}")
            failed += 1
    
    return passed, failed


def check_structure():
    """Check that expected directories exist."""
    print("\nChecking directory structure...")
    
    expected_dirs = [
        "backend",
        "backend/api",
        "backend/services",
        "backend/pipelines",
        "backend/models",
        "data",
        "data/ingestion",
        "data/validation",
        "data/features",
        "frontend",
        "tests",
        "scripts",
        "utils",
        "config",
        "docs",
    ]
    
    root = Path(__file__).parent.parent
    passed = 0
    failed = 0
    
    for dir_path in expected_dirs:
        full_path = root / dir_path
        if full_path.exists() and full_path.is_dir():
            print(f"  ✅ {dir_path}/")
            passed += 1
        else:
            print(f"  ❌ {dir_path}/ (missing)")
            failed += 1
    
    return passed, failed


def check_old_dirs():
    """Check that old directories are removed."""
    print("\nChecking old directories removed...")
    
    old_dirs = [
        "pgm_model",
        "analytics",
        "feature_engineering",
        "backtesting",
        "data_ingestion",
        "data_validation",
        "feature_store",
        "api",
        "services",
        "pipelines",
        "dashboard",
    ]
    
    root = Path(__file__).parent.parent
    found = []
    
    for dir_name in old_dirs:
        full_path = root / dir_name
        if full_path.exists():
            print(f"  ⚠️  {dir_name}/ still exists")
            found.append(dir_name)
        else:
            print(f"  ✅ {dir_name}/ removed")
    
    return len(old_dirs) - len(found), len(found)


def main():
    """Main verification function."""
    print("=" * 80)
    print("PROJECT STRUCTURE VERIFICATION")
    print("=" * 80)
    
    # Test imports
    import_passed, import_failed = test_imports()
    
    # Check structure
    struct_passed, struct_failed = check_structure()
    
    # Check old dirs removed
    old_passed, old_failed = check_old_dirs()
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Imports:        {import_passed} passed, {import_failed} failed")
    print(f"Structure:      {struct_passed} passed, {struct_failed} failed")
    print(f"Old dirs:       {old_passed} removed, {old_failed} remaining")
    
    total_passed = import_passed + struct_passed + old_passed
    total_failed = import_failed + struct_failed + old_failed
    
    print(f"\nTotal:          {total_passed} passed, {total_failed} failed")
    
    if total_failed == 0:
        print("\n✅ All checks passed! Structure refactoring successful.")
        return 0
    else:
        print(f"\n❌ {total_failed} checks failed. Please review.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
