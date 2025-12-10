from pydantic import BaseModel, validator


class Point(BaseModel):
    name: str

    @validator('name')
    def validate_name(cls, name) -> str:
        if not name or not isinstance(name, str) or name.strip() == "":
            raise ValueError("Name cannot be empty")
        return name