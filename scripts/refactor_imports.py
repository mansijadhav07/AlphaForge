#!/usr/bin/env python3
"""
Script to update imports after folder restructuring.
"""

import os
import re
from pathlib import Path

# Define import mappings
IMPORT_MAPPINGS = {
    # PGM model -> backend.models
    r'from pgm_model\.': 'from backend.models.',
    r'import pgm_model\.': 'import backend.models.',
    r'import pgm_model': 'import backend.models',
    
    # Analytics -> backend.models
    r'from analytics\.': 'from backend.models.',
    r'import analytics\.': 'import backend.models.',
    
    # Feature engineering -> backend.models
    r'from feature_engineering\.': 'from backend.models.',
    r'import feature_engineering\.': 'import backend.models.',
    
    # Backtesting -> backend.models
    r'from backtesting\.': 'from backend.models.',
    r'import backtesting\.': 'import backend.models.',
    
    # Data ingestion -> data.ingestion
    r'from data_ingestion\.': 'from data.ingestion.',
    r'import data_ingestion\.': 'import data.ingestion.',
    
    # Data validation -> data.validation
    r'from data_validation\.': 'from data.validation.',
    r'import data_validation\.': 'import data.validation.',
    
    # Feature store -> data.features
    r'from feature_store\.': 'from data.features.',
    r'import feature_store\.': 'import data.features.',
    
    # API -> backend.api
    r'from api\.': 'from backend.api.',
    r'import api\.': 'import backend.api.',
    
    # Services -> backend.services
    r'from services\.': 'from backend.services.',
    r'import services\.': 'import backend.services.',
    
    # Pipelines -> backend.pipelines
    r'from pipelines\.': 'from backend.pipelines.',
    r'import pipelines\.': 'import backend.pipelines.',
}


def update_imports_in_file(filepath: Path) -> bool:
    """Update imports in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply all mappings
        for old_pattern, new_pattern in IMPORT_MAPPINGS.items():
            content = re.sub(old_pattern, new_pattern, content)
        
        # Only write if changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False


def main():
    """Main function to update all imports."""
    root = Path(__file__).parent.parent
    
    # Files to update
    patterns = [
        'backend/**/*.py',
        'data/**/*.py',
        'tests/**/*.py',
        'scripts/**/*.py',
        'utils/**/*.py',
        'config/**/*.py',
        '*.py',  # Root level Python files
    ]
    
    updated_files = []
    
    for pattern in patterns:
        for filepath in root.glob(pattern):
            if filepath.is_file() and filepath.suffix == '.py':
                # Skip this script itself
                if filepath.name == 'refactor_imports.py':
                    continue
                
                if update_imports_in_file(filepath):
                    updated_files.append(str(filepath.relative_to(root)))
    
    print(f"\n✅ Updated {len(updated_files)} files:")
    for f in sorted(updated_files):
        print(f"   • {f}")
    
    if not updated_files:
        print("\n✅ No files needed updating")


if __name__ == '__main__':
    main()
