from pydantic import BaseModel

from app.dto.response.contact_response_dto import ContactResponseDto


class ContactListResponseDto(BaseModel):
    items: list[ContactResponseDto]
    page: int
    page_size: int
    has_previous: bool
    has_next: bool
    total: int | None = None
    total_pages: int | None = None
