from typing import Any
from typing import Optional

from pydantic import BaseModel

class BaseAPIResponse(BaseModel):
success: bool
message: str
data: Optional[Any] = None


class ErrorResponse(BaseModel):
success: bool = False
message: str
errors: Optional[list[str]] = None

