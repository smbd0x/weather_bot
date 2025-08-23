from pydantic import BaseModel, ConfigDict


class UserDTO(BaseModel):
    id: int
    username: str | None
    balance: int

    model_config = ConfigDict(from_attributes=True)
