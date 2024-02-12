import pydantic
from typing import Optional
from pydantic import BaseModel

class SelfComputerRequest(BaseModel):
    query: str = pydantic.Field(
        ..., title="Query", description="The query to pass to the provider"
    )
    summary: Optional[bool]= pydantic.Field(
        ..., title="Summary", description="Whether to generate a summary or not", value = False
    )
    # model: str = pydantic.Field(
    #     ..., title="Model", description="The model to use"
    # )

class WebhookResponse(BaseModel):
    key: str = pydantic.Field(
        ..., title="Key", description="The key to pass to the provider"
    )