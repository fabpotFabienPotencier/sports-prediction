from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime

class MatchData(BaseModel):
    match_id: str
    sport: str
    home_team: str
    away_team: str
    current_score: str
    time: str
    statistics: Dict[str, Any]

class PredictionRequest(BaseModel):
    match_id: str
    prediction_type: str  # "next_score", "match_outcome", etc.

class PredictionResponse(BaseModel):
    match_id: str
    prediction: str
    confidence: float
    timestamp: datetime
    match_data: MatchData
    additional_insights: Optional[Dict[str, Any]]

class ErrorResponse(BaseModel):
    detail: str
    error_code: str 