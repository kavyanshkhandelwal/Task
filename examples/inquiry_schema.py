"""Reference FastAPI/Pydantic schema for a public inquiry endpoint."""
from typing import Annotated
from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints, field_validator

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=100)]
Message = Annotated[str, StringConstraints(strip_whitespace=True, min_length=10, max_length=5000)]

class InquiryCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: Name
    email: EmailStr
    message: Message
    consent: bool
    source: Annotated[str | None, Field(max_length=80)] = None

    @field_validator("consent")
    @classmethod
    def consent_must_be_explicit(cls, value: bool) -> bool:
        if value is not True:
            raise ValueError("Consent is required to submit this inquiry.")
        return value

# Route-level controls still required:
# - authentication is intentionally not required for a public inquiry endpoint
# - request body size limit at proxy/application boundary
# - rate limit and bot controls
# - idempotency key + durable persistence
# - generic response; never echo submitted PII unnecessarily
