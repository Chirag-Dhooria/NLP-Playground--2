from pydantic import BaseModel
from typing import List, Optional, Any, Dict

class PreprocessRequest(BaseModel):
    filename: str
    text_column: str
    options: Dict[str, bool]  # e.g. {"lowercase": true, "lemmatization": true}

class TrainRequest(BaseModel):
    task_type: str  # "classification", "summarization", "qa", "sentiment"
    filename: str
    target_column: Optional[str] = None
    input_column: str
    hyperparameters: Optional[Dict[str, Any]] = {}
    context_column: Optional[str] = None # For QA

class ChatRequest(BaseModel):
    filename: str
    user_query: str

class RagQueryRequest(BaseModel):
    filename: str
    question: str
