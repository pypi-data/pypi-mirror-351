from pydantic import BaseModel


class Config(BaseModel):
    sleepyurl: str = "https://127.0.0.1:9010"