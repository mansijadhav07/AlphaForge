# Restart API Server - Quick Guide

## The Issue
The API server was running with old code. I've fixed the structure analysis bugs:
- Fixed `node_analysis` → `nodes` key mismatch
- Added missing `role` field to node info
- Fixed `key_nodes` transformation to extract node names

## How to Restart

### Step 1: Stop Current Server
In the terminal running `api_server.py`, press:
```
Ctrl + C
```

### Step 2: Restart Server
```bash
source venv/bin/activate
python3 api_server.py
```

### Step 3: Verify It Works
Open browser and go to:
```
http://localhost:3000/structure-analysis
```

You should now see:
- Network summary cards (nodes, edges, DAG status)
- Correlation heatmap
- 13 edge explanations with details

## What Was Fixed

1. **Key mismatch**: Changed `node_analysis` to `nodes` in return dict
2. **Missing role field**: Added `role` to each node using `_determine_node_role()`
3. **Key nodes format**: Extract node names from dict list

## Test Command
```bash
curl 'http://localhost:8000/api/pgm/structure-analysis?symbol=AAPL' | python3 -m json.tool
```

Should return JSON with correlation_matrix, dependency_analysis, edge_explanations, etc.
