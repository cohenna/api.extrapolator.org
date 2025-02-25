from datetime import datetime
from uuid import uuid4
from sqlmodel import Field, SQLModel

class Extrapolation(SQLModel, table=True):
    uuid: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    input: str
    extrapolation: str
    timestamp: datetime = Field(default_factory=datetime.now, index=True)

