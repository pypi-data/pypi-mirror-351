from pydantic import Field
from typing import Optional
from datetime import datetime
from abs_nosql_repository_core.document.base_document import BaseDocument


class Integration(BaseDocument):
    provider_name: Optional[str] = Field(None, description="The name of the provider")
    access_token: Optional[str] = Field(None, description="The access token")
    refresh_token: Optional[str] = Field(None, description="The refresh token")
    expires_at: Optional[datetime] = Field(None, description="The expiration date of the access token")

    class Settings:
        name = "integrations"

    def model_dump_for_update(self):
        return self.model_dump(
            exclude_none=True,
            exclude={"created_at", "id", "uuid", "provider_name"}
        )
