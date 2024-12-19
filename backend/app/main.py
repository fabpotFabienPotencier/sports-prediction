from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from prometheus_client import make_asgi_app

from app.api.endpoints import soccer, basketball, tennis
from app.core.prediction_engine import PredictionEngine
from app.utils.logger import setup_logging
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="Live Sports Prediction Bot using GPT-4",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Include routers
app.include_router(soccer.router, prefix="/predict/soccer", tags=["soccer"])
app.include_router(basketball.router, prefix="/predict/basketball", tags=["basketball"])
app.include_router(tennis.router, prefix="/predict/tennis", tags=["tennis"])

@app.on_event("startup")
async def startup():
    # Initialize cache
    redis = aioredis.from_url(settings.REDIS_URL, encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    
    # Setup logging
    setup_logging()

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 