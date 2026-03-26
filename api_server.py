"""
FastAPI server for AlphaForge API.

Exposes REST APIs for PGM predictions and other features.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from api.pgm_routes import router as pgm_router
from api.market_routes import router as market_router
from api.discretization_routes import router as discretization_router
from api.dependencies import initialize_pgm_service
from utils.logger import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    
    Initializes PGM service on startup.
    """
    # Startup
    logger.info("Starting AlphaForge API server...")
    
    try:
        # Initialize PGM service
        logger.info("Initializing PGM service...")
        initialize_pgm_service()
        logger.info("PGM service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize PGM service: {e}", exc_info=True)
        logger.warning("API will start but PGM endpoints may not work until data is available")
    
    logger.info("AlphaForge API server started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AlphaForge API server...")


# Create FastAPI app
app = FastAPI(
    title="AlphaForge API",
    description="""
    **AlphaForge - Real-Time Financial Feature Intelligence Platform**
    
    Production-grade API for probabilistic market predictions using Bayesian Networks.
    
    ## Features
    
    * **Probabilistic Predictions** - Get probability distributions for market outcomes
    * **Explainable AI** - Understand why predictions are made
    * **Trading Signals** - BUY/SELL/HOLD recommendations with confidence levels
    * **Scenario Simulation** - Test what-if scenarios
    * **Feature Impact** - Analyze which features drive predictions
    * **Market Regime** - Identify bull/bear/sideways markets
    * **Graph Structure** - Visualize feature dependencies
    
    ## Getting Started
    
    1. Ensure you have run `example_workflow.py` to generate training data
    2. The PGM model will be automatically trained on first API call
    3. Use `/api/pgm/health` to check service status
    4. Try `/api/pgm/probabilities/AAPL` for a quick test
    
    ## Authentication
    
    Currently no authentication required (development mode).
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(pgm_router)
app.include_router(market_router)
app.include_router(discretization_router)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "name": "AlphaForge API",
        "version": "1.0.0",
        "description": "Real-Time Financial Feature Intelligence Platform",
        "docs": "/docs",
        "health": "/api/pgm/health",
        "endpoints": {
            "probabilities": "/api/pgm/probabilities/{symbol}",
            "explanation": "/api/pgm/explanation/{symbol}",
            "signal": "/api/pgm/signal/{symbol}",
            "simulate": "/api/pgm/simulate",
            "feature_impact": "/api/pgm/feature-impact/{symbol}",
            "regime": "/api/pgm/regime/{symbol}",
            "graph": "/api/pgm/graph"
        }
    }


# Health check
@app.get("/health", tags=["Health"])
async def health():
    """
    General health check endpoint.
    """
    return {
        "status": "healthy",
        "service": "AlphaForge API",
        "version": "1.0.0"
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Endpoint not found",
            "path": str(request.url.path)
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc)
        }
    )


def run_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
    log_level: str = "info"
):
    """
    Run the FastAPI server.
    
    Args:
        host: Host to bind to
        port: Port to bind to
        reload: Enable auto-reload for development
        log_level: Logging level
    """
    logger.info(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        "api_server:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
        access_log=True
    )


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AlphaForge API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--log-level", default="info", help="Log level")
    
    args = parser.parse_args()
    
    run_server(
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level
    )
