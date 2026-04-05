from pydantic import BaseModel


class ContactImportErrorDto(BaseModel):
    row: int
    message: str
    email: str | None = None


class ContactImportResponseDto(BaseModel):
    total_rows: int
    imported_count: int
    skipped_count: int
    errors: list[ContactImportErrorDto]
