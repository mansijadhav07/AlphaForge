# Makefile for Financial Feature Store

.PHONY: help install setup clean test run-batch run-stream dashboard status

help:
	@echo "Financial Feature Store - Available Commands"
	@echo "=============================================="
	@echo ""
	@echo "Setup:"
	@echo "  make install      - Install dependencies"
	@echo "  make setup        - Complete setup (venv + install + redis check)"
	@echo ""
	@echo "Run:"
	@echo "  make run-batch    - Run batch pipeline (full)"
	@echo "  make run-stream   - Run streaming pipeline"
	@echo "  make dashboard    - Launch dashboard"
	@echo "  make example      - Run example workflow"
	@echo ""
	@echo "Utilities:"
	@echo "  make status       - Show system status"
	@echo "  make clean        - Clean generated files"
	@echo "  make test         - Run tests"
	@echo ""

install:
	pip install -r requirements.txt

setup:
	@echo "Setting up Financial Feature Store..."
	python -m venv venv || true
	@echo "Virtual environment created. Activate with: source venv/bin/activate"
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	@echo "Checking Redis..."
	@redis-cli ping || echo "Warning: Redis not running. Start with: redis-server"
	@echo "Setup complete!"

clean:
	@echo "Cleaning generated files..."
	rm -rf data/
	rm -rf logs/
	rm -rf __pycache__/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	@echo "Clean complete!"

test:
	pytest tests/ -v

run-batch:
	python main.py batch --mode full --tickers AAPL,TSLA,GOOGL

run-incremental:
	python main.py batch --mode incremental --lookback-days 5

run-stream:
	python main.py stream --interval 60 --max-iterations 10

dashboard:
	python main.py dashboard

status:
	python main.py status

example:
	python example_workflow.py

analytics:
	python main.py analytics --ticker AAPL --plots

backtest:
	python -m backtesting.backtest_engine --strategy all --ticker AAPL

format:
	black .
	flake8 . --max-line-length=120

redis-start:
	redis-server &

redis-stop:
	redis-cli shutdown

redis-check:
	@redis-cli ping && echo "Redis is running" || echo "Redis is not running"
