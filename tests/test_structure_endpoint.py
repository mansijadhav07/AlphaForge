#!/usr/bin/env python3
"""
Test script for structure analysis endpoint.
"""

import requests
import json

def test_structure_analysis():
    """Test the structure analysis endpoint."""
    url = "http://localhost:8000/api/pgm/structure-analysis"
    params = {"symbol": "AAPL"}
    
    print("Testing structure analysis endpoint...")
    print(f"URL: {url}")
    print(f"Params: {params}")
    print("-" * 80)
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print("-" * 80)
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Success!")
            print("\nResponse structure:")
            print(f"  - Timestamp: {data.get('timestamp')}")
            print(f"  - Correlation Matrix: {len(data.get('correlation_matrix', {}).get('features', []))} features")
            print(f"  - Dependency Analysis: {len(data.get('dependency_analysis', {}).get('nodes', {}))} nodes")
            print(f"  - Edge Explanations: {len(data.get('edge_explanations', []))} edges")
            print(f"  - Network Summary: {data.get('network_summary', {}).get('total_nodes')} nodes, {data.get('network_summary', {}).get('total_edges')} edges")
            
            # Print first edge explanation as example
            if data.get('edge_explanations'):
                print("\nExample Edge Explanation:")
                edge = data['edge_explanations'][0]
                print(f"  {edge['parent']} → {edge['child']}")
                print(f"  Type: {edge['edge_type']}")
                print(f"  Strength: {edge['strength']}")
                print(f"  Reasoning: {edge['reasoning'][:100]}...")
            
            return True
        else:
            print(f"✗ Error: {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Error: Could not connect to server")
        print("Make sure the API server is running: python3 api_server.py")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


if __name__ == "__main__":
    success = test_structure_analysis()
    exit(0 if success else 1)
