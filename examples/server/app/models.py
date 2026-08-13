from pydantic import BaseModel, Field

class UserDTO(BaseModel):
    id: int = Field(..., description="Unique user identifier")
    username: str = Field(..., description="Unique handle for user profile")
