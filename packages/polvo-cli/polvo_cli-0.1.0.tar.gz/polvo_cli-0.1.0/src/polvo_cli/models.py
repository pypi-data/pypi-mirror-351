from typing import List, Optional
from pydantic import BaseModel


class EvaluationRequest(BaseModel):
    """Request model for embedding evaluation."""
    texts: List[str]
    models: List[str]
    queries: Optional[List[str]] = None 