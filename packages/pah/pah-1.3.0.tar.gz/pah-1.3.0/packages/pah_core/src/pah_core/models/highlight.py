from pydantic import BaseModel, Field


class Highlight(BaseModel):
    page: int = Field(..., description="Page number")
    text: str = Field(..., description="Highlighted text")
    reason: str = Field(..., description="Reason for highlighting the text")
    color: str = Field(
        ..., description="Color of the highlight (e.g., 'yellow' or '#FFFF00')"
    )
