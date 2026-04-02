#!/usr/bin/env python3
"""
Local test for structure analysis to verify it works before restarting server.
"""

import sys
import pandas as pd
import numpy as np

# Add project to path
sys.path.insert(0, '.')

from backend.models.structure_analysis import StructureAnalyzer

def test_structure_analysis():
    """Test structure analysis locally."""
    print("Testing structure analysis...")
    print("-" * 80)
    
    # Create analyzer
    analyzer = StructureAnalyzer()
    
    # Generate mock data
    np.random.seed(42)
    n_samples = 100
    
    mock_data = pd.DataFrame({
        'RSI': np.random.uniform(20, 80, n_samples),
        'MACD': np.random.normal(0, 2, n_samples),
        'BB_width': np.random.uniform(0.01, 0.05, n_samples),
        'volume_ratio': np.random.uniform(0.5, 2.0, n_samples),
        'ATR': np.random.uniform(0.5, 3.0, n_samples),
    })
    
    try:
        # Test generate_structure_report
        print("1. Testing generate_structure_report()...")
        report = analyzer.generate_structure_report(mock_data)
        
        print(f"   ✓ Report generated")
        print(f"   - Keys: {list(report.keys())}")
        
        # Check required keys
        required_keys = [
            'timestamp',
            'correlation_matrix',
            'dependency_analysis',
            'edge_explanations',
            'structure_validation',
            'network_summary'
        ]
        
        for key in required_keys:
            if key in report:
                print(f"   ✓ {key}: present")
            else:
                print(f"   ✗ {key}: MISSING")
                return False
        
        # Check structure_validation keys
        print("\n2. Checking structure_validation keys...")
        val = report['structure_validation']
        val_keys = ['is_valid_dag', 'has_cycles', 'correlation_support', 'missing_edges', 'validation_summary']
        
        for key in val_keys:
            if key in val:
                print(f"   ✓ {key}: {val[key] if key != 'correlation_support' else f'{len(val[key])} edges'}")
            else:
                print(f"   ✗ {key}: MISSING")
                return False
        
        # Check dependency_analysis keys
        print("\n3. Checking dependency_analysis keys...")
        dep = report['dependency_analysis']
        dep_keys = ['nodes', 'key_nodes', 'dependency_paths']
        
        for key in dep_keys:
            if key in dep:
                if key == 'nodes':
                    print(f"   ✓ {key}: {len(dep[key])} nodes")
                elif key == 'key_nodes':
                    print(f"   ✓ {key}: {dep[key]}")
                else:
                    print(f"   ✓ {key}: {len(dep[key])} paths")
            else:
                print(f"   ✗ {key}: MISSING")
                return False
        
        # Check node structure
        print("\n4. Checking node structure...")
        first_node_key = list(dep['nodes'].keys())[0]
        first_node = dep['nodes'][first_node_key]
        node_keys = ['name', 'parents', 'children', 'role']
        
        for key in node_keys:
            if key in first_node:
                print(f"   ✓ {key}: present")
            else:
                print(f"   ✗ {key}: MISSING")
                return False
        
        print("\n" + "=" * 80)
        print("✓ ALL TESTS PASSED!")
        print("=" * 80)
        print("\nYou can now restart the API server:")
        print("  1. Press Ctrl+C in the terminal running api_server.py")
        print("  2. Run: source venv/bin/activate")
        print("  3. Run: python3 api_server.py")
        print("  4. Refresh: http://localhost:3000/structure-analysis")
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_structure_analysis()
    sys.exit(0 if success else 1)
