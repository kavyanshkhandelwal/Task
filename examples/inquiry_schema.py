"""Illustrative FastAPI request schema; not Cynbit production code."""
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class InquiryCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    company: str | None = Field(default=None, max_length=120)
    project_type: str = Field(min_length=2, max_length=40)
    message: str = Field(min_length=20, max_length=5000)
    consent: bool

    @field_validator("consent")
    @classmethod
    def consent_must_be_explicit(cls, value: bool) -> bool:
        if value is not True:
            raise ValueError("Consent is required to submit this inquiry.")
        return value
