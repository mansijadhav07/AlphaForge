# Folder Reorganization Guide 📁

## Current Issue
Documentation files are scattered in the root directory, making it hard to navigate.

## Proposed Clean Structure

```
AlphaForge/
├── 📄 README.md                    # Main project README
├── 📄 LICENSE                      # License file
├── 📄 .gitignore                   # Git ignore
├── 📄 requirements.txt             # Python dependencies
├── 📄 Makefile                     # Build commands
│
├── 📁 docs/                        # 📚 ALL DOCUMENTATION
│   ├── README.md                   # Documentation index
│   ├── setup/                      # Installation guides
│   │   ├── INSTALLATION.md
│   │   └── QUICKSTART.md
│   ├── overview/                   # Project overview
│   │   ├── PROJECT_SUMMARY.md
│   │   ├── FEATURES.md
│   │   └── PROJECT_ANALYSIS.md
│   ├── architecture/               # Architecture docs
│   │   └── ARCHITECTURE.md
│   ├── pgm/                       # PGM documentation
│   │   ├── WHAT_IS_PGM.md
│   │   ├── PGM_DOCUMENTATION.md
│   │   ├── PGM_INTEGRATION_GUIDE.md
│   │   ├── PGM_MODULE_SUMMARY.md
│   │   └── PGM_COMPLETION_REPORT.md
│   ├── features/                  # Feature docs
│   │   ├── PGM_GRAPH_SUMMARY.md
│   │   ├── FEATURE_CONTRIBUTION_COMPLETE.md
│   │   ├── MODEL_EVALUATION_COMPLETE.md
│   │   └── FAILURE_ANALYSIS_COMPLETE.md
│   └── performance/               # Performance docs
│       ├── PERFORMANCE_FIXES.md
│       └── PERFORMANCE_GUIDE.md
│
├── 📁 src/                        # 🐍 PYTHON SOURCE CODE
│   ├── pgm_model/                 # PGM modules
│   ├── api/                       # FastAPI backend
│   ├── feature_engineering/       # Feature computation
│   ├── feature_store/             # Storage
│   ├── data_ingestion/            # Data fetching
│   ├── data_validation/           # Data quality
│   ├── backtesting/               # Strategy testing
│   ├── analytics/                 # Analysis
│   ├── pipelines/                 # Data pipelines
│   ├── dashboard/                 # Streamlit (legacy)
│   ├── utils/                     # Utilities
│   └── config/                    # Configuration
│
├── 📁 frontend/                   # ⚛️ NEXT.JS FRONTEND
│   ├── app/                       # Pages
│   ├── components/                # React components
│   ├── lib/                       # Utilities
│   ├── public/                    # Static files
│   ├── README.md                  # Frontend docs
│   └── package.json
│
├── 📁 scripts/                    # 🔧 UTILITY SCRIPTS
│   ├── example_workflow.py        # Example usage
│   ├── example_pgm_workflow.py    # PGM example
│   └── demo_pgm.py                # PGM demo
│
├── 📁 tests/                      # 🧪 UNIT TESTS
│   ├── test_pgm_module.py
│   └── test_ingestion.py
│
├── 📁 data/                       # 💾 DATA STORAGE (gitignored)
│   ├── raw/
│   ├── features/
│   ├── validated/
│   ├── analytics/
│   └── backtesting/
│
├── 📁 logs/                       # 📝 LOG FILES (gitignored)
│
└── 📄 api_server.py               # Main API server entry point
```

## Step-by-Step Reorganization

### Option 1: Manual Reorganization (Recommended)

**Step 1: Create folder structure**
```bash
mkdir -p docs/{setup,overview,architecture,pgm,features,performance}
mkdir -p src
mkdir -p scripts
```

**Step 2: Move documentation files**
```bash
# Setup docs
mv INSTALLATION_STEPS.md docs/setup/INSTALLATION.md
mv QUICKSTART.md docs/setup/QUICKSTART.md

# Overview docs
mv PROJECT_SUMMARY.md docs/overview/
mv FEATURES.md docs/overview/
mv PROJECT_ANALYSIS.md docs/overview/

# Architecture
mv ARCHITECTURE.md docs/architecture/

# PGM docs
mv WHAT_IS_PGM.md docs/pgm/
mv PGM_DOCUMENTATION.md docs/pgm/
mv PGM_INTEGRATION_GUIDE.md docs/pgm/
mv PGM_MODULE_SUMMARY.md docs/pgm/
mv PGM_COMPLETION_REPORT.md docs/pgm/

# Feature docs
mv PGM_GRAPH_SUMMARY.md docs/features/
mv FEATURE_CONTRIBUTION_COMPLETE.md docs/features/
mv MODEL_EVALUATION_COMPLETE.md docs/features/
mv FAILURE_ANALYSIS_COMPLETE.md docs/features/

# Performance docs
mv PERFORMANCE_FIXES.md docs/performance/
# Note: PERFORMANCE_GUIDE.md is in frontend/
```

**Step 3: Move Python source code**
```bash
# Move all Python modules to src/
mv pgm_model src/
mv api src/
mv feature_engineering src/
mv feature_store src/
mv data_ingestion src/
mv data_validation src/
mv backtesting src/
mv analytics src/
mv pipelines src/
mv dashboard src/
mv utils src/
mv config src/
```

**Step 4: Move scripts**
```bash
mv example_workflow.py scripts/
mv example_pgm_workflow.py scripts/
mv demo_pgm.py scripts/
mv main.py scripts/  # If not used as entry point
```

**Step 5: Update imports**

After moving to `src/`, you'll need to update imports. Add this to the root:

Create `src/__init__.py`:
```python
# Empty file to make src a package
```

Update imports in all files from:
```python
from pgm_model import something
```
to:
```python
from src.pgm_model import something
```

### Option 2: Keep Current Structure (Simpler)

If you want to avoid breaking imports, just organize documentation:

```bash
# Only move documentation
mkdir -p docs/{setup,overview,architecture,pgm,features,performance}

# Move docs (commands above)
# Keep all Python code in root
```

## Recommended Approach

**For now, I recommend Option 2** (organize docs only) because:
1. ✅ No import changes needed
2. ✅ No risk of breaking code
3. ✅ Cleaner documentation structure
4. ✅ Easy to implement

**Later, you can do Option 1** when you have time to:
1. Update all imports
2. Update `api_server.py`
3. Update `requirements.txt` paths
4. Test everything works

## Quick Commands (Option 2 - Docs Only)

```bash
# Create docs structure
mkdir -p docs/{setup,overview,architecture,pgm,features,performance}

# Move documentation files
mv INSTALLATION_STEPS.md docs/setup/INSTALLATION.md
mv QUICKSTART.md docs/setup/QUICKSTART.md
mv PROJECT_SUMMARY.md docs/overview/
mv FEATURES.md docs/overview/
mv PROJECT_ANALYSIS.md docs/overview/
mv ARCHITECTURE.md docs/architecture/
mv WHAT_IS_PGM.md docs/pgm/
mv PGM_DOCUMENTATION.md docs/pgm/
mv PGM_INTEGRATION_GUIDE.md docs/pgm/
mv PGM_INTEGRATION_GUIDE.md docs/pgm/
mv PGM_MODULE_SUMMARY.md docs/pgm/
mv PGM_COMPLETION_REPORT.md docs/pgm/
mv PGM_GRAPH_SUMMARY.md docs/features/
mv FEATURE_CONTRIBUTION_COMPLETE.md docs/features/
mv MODEL_EVALUATION_COMPLETE.md docs/features/
mv FAILURE_ANALYSIS_COMPLETE.md docs/features/
mv PERFORMANCE_FIXES.md docs/performance/

# Update README to point to docs/
```

## After Reorganization

Update the main `README.md` to point to the new docs location:

```markdown
## 📖 Documentation

All documentation is in the [`docs/`](./docs/) folder:

- [Installation Guide](./docs/setup/INSTALLATION.md)
- [Quick Start](./docs/setup/QUICKSTART.md)
- [Architecture](./docs/architecture/ARCHITECTURE.md)
- [PGM Documentation](./docs/pgm/PGM_DOCUMENTATION.md)
- [Features](./docs/overview/FEATURES.md)
- [Performance Guide](./docs/performance/PERFORMANCE_GUIDE.md)

See [docs/README.md](./docs/README.md) for complete documentation index.
```

## Benefits of Clean Structure

✅ **Easier Navigation** - Find docs quickly  
✅ **Professional** - Industry standard structure  
✅ **Scalable** - Easy to add new docs  
✅ **Clear Separation** - Code vs docs vs tests  
✅ **Better Git** - Cleaner diffs  
✅ **IDE Friendly** - Better autocomplete  

## What to Keep in Root

Only these files should be in root:
- `README.md` - Main project README
- `LICENSE` - License file
- `.gitignore` - Git ignore
- `requirements.txt` - Dependencies
- `Makefile` - Build commands
- `api_server.py` - Main entry point
- `package.json` - If using npm scripts
- `.env.example` - Environment template

Everything else goes in organized folders!

---

**Ready to reorganize?** Start with Option 2 (docs only) for a quick win!
