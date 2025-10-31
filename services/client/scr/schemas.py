from pydantic import BaseModel
from typing import Optional

class TranslateRequest(BaseModel):
    text: str
    source_lang: str
    target_lang: str
    request_id: Optional[str] = None

class TranslateResponse(BaseModel):
    request_id: str
    original_text: str
    translated_text: str
    source_lang: str
    target_lang: str