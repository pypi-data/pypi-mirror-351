from abs_nosql_repository_core.document.base_document import BaseDraftDocument
from pydantic import Field
from datetime import datetime


class IntegrationDocument(BaseDraftDocument):
    provider_name: str = Field(..., description="The name of the provider")
    access_token: str = Field(..., description="The access token")
    refresh_token: str = Field(..., description="The refresh token")
    expires_at: datetime = Field(..., description="The expiration date of the access token")

    class Settings:
        name = "integrations"
