from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class AuthIdentity:
    provider: str
    subject: str
    email: str | None
    claims: Mapping[str, object]
