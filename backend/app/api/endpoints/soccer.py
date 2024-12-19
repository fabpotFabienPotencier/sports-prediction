from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from app.core.prediction_engine import PredictionEngine
from app.core.data_fetcher import SportDataFetcher
from app.models.schemas import PredictionRequest, PredictionResponse
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post("/predict", response_model=PredictionResponse)
async def predict_soccer(
    request: PredictionRequest,
    prediction_engine: PredictionEngine = Depends(),
    data_fetcher: SportDataFetcher = Depends()
):
    try:
        # Fetch live match data
        match_data = await data_fetcher.get_live_match_data("soccer", request.match_id)
        
        # Generate prediction
        prediction = await prediction_engine.generate_prediction("soccer", match_data)
        
        return PredictionResponse(
            match_id=request.match_id,
            prediction=prediction["prediction"],
            confidence=prediction["confidence"],
            timestamp=prediction["timestamp"],
            match_data=match_data,
            additional_insights=prediction.get("additional_insights")
        )
    except Exception as e:
        logger.error(f"Error in soccer prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/live/{match_id}", response_model=Dict[str, Any])
async def get_live_soccer_data(
    match_id: str,
    data_fetcher: SportDataFetcher = Depends()
):
    try:
        return await data_fetcher.get_live_match_data("soccer", match_id)
    except Exception as e:
        logger.error(f"Error fetching soccer data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 