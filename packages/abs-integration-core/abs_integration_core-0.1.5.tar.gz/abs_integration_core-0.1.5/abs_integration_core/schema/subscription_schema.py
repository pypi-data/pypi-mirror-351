from pydantic import BaseModel, Field

class Subscription(BaseModel):
    resource_type: str
    site_id: str
    resource_id: str
    change_type: str

    class Config:
        extra = "allow"


class SubscribeRequestSchema(BaseModel):
    resource_type: str = Field(..., description="Type of resource: 'list' or 'drive'")
    site_id: str = Field(..., description="SharePoint site ID")
    resource_id: str = Field(..., description="List or Drive ID")
    change_type: str = Field("updated", description="Change types to subscribe to")
    expiration_days: int = Field(15, description="Subscription expiration in days (max 30)")
    automation_id: str = Field(..., description="Automation ID")
