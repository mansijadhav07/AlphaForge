# Installation Guide

## System Requirements

### Minimum Requirements
- **OS**: macOS, Linux, or Windows 10+
- **Python**: 3.10 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 2GB for dependencies + data storage
- **Internet**: Required for data fetching

### Optional Requirements
- **Redis**: For online feature store (recommended)
- **Docker**: For containerized deployment (optional)

## Installation Steps

### 1. Clone or Download Project

```bash
# If using git
git clone <repository-url>
cd project

# Or download and extract ZIP
```

### 2. Create Virtual Environment

#### macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- pandas, numpy (data processing)
- yfinance (data ingestion)
- ta (technical analysis)
- matplotlib, plotly, seaborn (visualization)
- streamlit (dashboard)
- redis (online store)
- loguru (logging)
- pytest (testing)

### 4. Install Redis (Optional but Recommended)

#### macOS
```bash
brew install redis
brew services start redis
```

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### Windows
```bash
# Download from: https://github.com/microsoftarchive/redis/releases
# Or use Docker:
docker run -d -p 6379:6379 redis:latest
```

#### Verify Redis Installation
```bash
redis-cli ping
# Should return: PONG
```

### 5. Verify Installation

```bash
# Check Python version
python --version  # Should be 3.10+

# Check installed packages
pip list | grep pandas
pip list | grep streamlit

# Test imports
python -c "import pandas; import yfinance; import streamlit; print('All imports successful!')"
```

### 6. Configure the System

```bash
# Configuration file is already created at:
# config/config.yaml

# Review and modify if needed:
# - Tickers to track
# - Date ranges
# - Storage locations
# - Redis connection settings
```

### 7. Create Required Directories

```bash
# These will be created automatically, but you can create them manually:
mkdir -p data/raw
mkdir -p data/validated
mkdir -p data/features/offline
mkdir -p data/analytics
mkdir -p data/backtesting
mkdir -p logs
```

## Quick Test

### Test Data Ingestion
```bash
python -c "
from data_ingestion import DataIngestion
ing = DataIngestion(tickers=['AAPL'], start_date='2024-01-01', end_date='2024-01-31')
df = ing.fetch_single_ticker('AAPL', save=False)
print(f'Success! Retrieved {len(df)} records')
"
```

### Test Redis Connection
```bash
python -c "
from feature_store import OnlineFeatureStore
store = OnlineFeatureStore()
print('Redis connected!' if store.is_connected() else 'Redis not available')
"
```

### Run Example Workflow
```bash
python example_workflow.py
```

## Troubleshooting

### Issue: Python version too old
```bash
# Install Python 3.10+ from python.org
# Or use pyenv:
pyenv install 3.10.0
pyenv local 3.10.0
```

### Issue: pip install fails
```bash
# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install packages one by one to identify issues
pip install pandas
pip install yfinance
# etc.
```

### Issue: Redis connection error
```bash
# Check if Redis is running
redis-cli ping

# Start Redis
# macOS: brew services start redis
# Linux: sudo systemctl start redis-server
# Windows: Start Redis service or Docker container

# Check Redis port
redis-cli -p 6379 ping
```

### Issue: yfinance data fetch fails
```bash
# This is usually a temporary issue
# Try again after a few minutes
# Or check your internet connection
# yfinance sometimes has rate limits
```

### Issue: Import errors
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

### Issue: Permission denied
```bash
# macOS/Linux: Use sudo for system-wide installs
sudo pip install -r requirements.txt

# Or install in user directory
pip install --user -r requirements.txt
```

## Platform-Specific Notes

### macOS
- Use Homebrew for Redis installation
- Python 3 is usually available as `python3`
- May need Xcode Command Line Tools: `xcode-select --install`

### Linux
- Use apt/yum for Redis installation
- May need to install python3-venv: `sudo apt-get install python3-venv`
- Check firewall settings for Redis port 6379

### Windows
- Use Windows Subsystem for Linux (WSL) for best experience
- Or use Docker for Redis
- May need Visual C++ Build Tools for some packages

## Docker Installation (Alternative)

### Create Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py", "status"]
```

### Build and Run
```bash
docker build -t financial-feature-store .
docker run -it financial-feature-store
```

### Docker Compose (with Redis)
```yaml
version: '3.8'
services:
  app:
    build: .
    volumes:
      - ./data:/app/data
    depends_on:
      - redis
  
  redis:
    image: redis:latest
    ports:
      - "6379:6379"
```

## Next Steps

After successful installation:

1. **Read Documentation**
   - README.md - Overview
   - QUICKSTART.md - Quick start guide
   - ARCHITECTURE.md - System architecture

2. **Run First Pipeline**
   ```bash
   python main.py batch --mode full --tickers AAPL
   ```

3. **Launch Dashboard**
   ```bash
   python main.py dashboard
   ```

4. **Explore Examples**
   ```bash
   python example_workflow.py
   ```

## Getting Help

- Check logs in `./logs/` directory
- Review error messages carefully
- Ensure all dependencies are installed
- Verify Redis is running (if using online store)
- Check Python version compatibility

## Uninstallation

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf venv

# Remove data (optional)
rm -rf data logs

# Stop Redis (if installed)
# macOS: brew services stop redis
# Linux: sudo systemctl stop redis-server
```

## Support

For issues and questions:
1. Check documentation files
2. Review error logs
3. Verify installation steps
4. Check system requirements
