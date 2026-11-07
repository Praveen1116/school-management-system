from pydantic import BaseModel, Field

class SetupRequest(BaseModel):
    school_name: str = Field(..., min_length=2, max_length=255)
    school_code: str = Field(..., min_length=2, max_length=50)
    full_name: str = Field(..., min_length=2, max_length=255)
    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=6)

class SetupStatusResponse(BaseModel):
    is_setup_required: bool
    school_name: str | None = None
    school_code: str | None = None

class SetupResponse(BaseModel):
    school_name: str
    school_code: str
    admin_email: str
    admin_name: str
