from abs_nosql_repository_core.repository.base_repository import BaseRepository
from abs_nosql_integration_core.model.integration_model import IntegrationDocument
from abs_nosql_integration_core.schema import CreateIntegration, TokenData, Integration
from abs_nosql_integration_core.schema.integration_schema import Integration
from abs_nosql_integration_core.schema.integration_schema import Integration

class IntegrationRepository(BaseRepository):
    def __init__(self):
        super().__init__(document=IntegrationDocument)

    async def create_integration(self, integration_data: CreateIntegration) -> Integration:
        """
        Create a new integration record.
        
        Args:
            integration_data: Integration data including provider_name, access_token, etc.
            
        Returns:
            The created integration object
            
        Raises:
            DuplicatedError: If integration with same provider already exists
        """
        new_integration = Integration(
            provider_name=integration_data.provider_name,
            access_token=integration_data.access_token,
            refresh_token=integration_data.refresh_token,
            expires_at=integration_data.expires_at,
        ).model_dump(exclude_none=True)

        integration = await super().create(new_integration)
        return integration

    async def refresh_token(
        self,
        provider_name: str, 
        token_data: TokenData
    ) -> Integration:
        """
        Update token information for a specific integration.
        
        Args:
            provider_name: The integration provider name
            token_data: The data to update
            
        Returns:
            The updated integration object
            
        Raises:
            NotFoundError: If integration doesn't exist
        """
        integration = await super().get_by_attr(
            attr="provider_name",
            value=provider_name
        )

        integration_data = await super().update(integration["id"], token_data.model_dump(exclude_none=True))

        return integration_data
