from pydantic import BaseModel


class GroupRead(BaseModel):
    slug: str
    name: str

    model_config = {"from_attributes": True}
