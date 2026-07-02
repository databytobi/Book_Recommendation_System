from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    page: int = Field(
        default=1,
        ge=1
    )

    size: int = Field(
        default=20,
        ge=1,
        le=100
    )


class PaginationMeta(BaseModel):
    page: int
    size: int
    total: int
    total_pages: int