#!/bin/bash

# AlphaForge Redis Setup Script
# Helps install and configure Redis for optimal performance

set -e

echo "🚀 AlphaForge Redis Setup"
echo "========================="
echo ""

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
else
    OS="unknown"
fi

echo "Detected OS: $OS"
echo ""

# Check if Redis is already installed
if command -v redis-server &> /dev/null; then
    echo "✅ Redis is already installed"
    redis-server --version
    echo ""
    
    # Check if Redis is running
    if redis-cli ping &> /dev/null; then
        echo "✅ Redis is running"
        echo ""
        echo "Redis info:"
        redis-cli INFO server | grep redis_version
        redis-cli INFO memory | grep used_memory_human
    else
        echo "⚠️  Redis is installed but not running"
        echo ""
        
        if [[ "$OS" == "macos" ]]; then
            echo "Start Redis with:"
            echo "  brew services start redis"
        elif [[ "$OS" == "linux" ]]; then
            echo "Start Redis with:"
            echo "  sudo systemctl start redis"
        fi
    fi
else
    echo "❌ Redis is not installed"
    echo ""
    echo "Installation options:"
    echo ""
    
    if [[ "$OS" == "macos" ]]; then
        echo "Option 1: Install with Homebrew (recommended)"
        echo "  brew install redis"
        echo "  brew services start redis"
        echo ""
        echo "Option 2: Install with Docker"
        echo "  docker run -d -p 6379:6379 --name redis redis:alpine"
        
    elif [[ "$OS" == "linux" ]]; then
        echo "Option 1: Install with apt (Ubuntu/Debian)"
        echo "  sudo apt-get update"
        echo "  sudo apt-get install redis-server"
        echo "  sudo systemctl start redis"
        echo ""
        echo "Option 2: Install with Docker"
        echo "  docker run -d -p 6379:6379 --name redis redis:alpine"
        
    else
        echo "Option: Install with Docker"
        echo "  docker run -d -p 6379:6379 --name redis redis:alpine"
    fi
    
    echo ""
    echo "Note: AlphaForge will work without Redis using in-memory cache,"
    echo "but Redis is recommended for production use."
fi

echo ""
echo "========================="
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Install Redis (if not already installed)"
echo "2. Start Redis server"
echo "3. Install Python dependencies: pip install redis"
echo "4. Start AlphaForge backend: python api_server.py"
echo ""
echo "The cache service will automatically detect and use Redis."
echo "If Redis is unavailable, it will fall back to in-memory cache."
