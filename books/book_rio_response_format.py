from pydantic import BaseModel
from typing import List


class BookROIResponseFormat(BaseModel):
    roi_score: int
    match_reasoning: str
    relevant_takeaways: List[str]
    time_analysis: str
    estimated_reading_hours: float
    recommendation: str
