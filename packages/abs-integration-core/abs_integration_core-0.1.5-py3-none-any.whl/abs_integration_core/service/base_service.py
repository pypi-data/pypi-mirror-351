from abc import ABC, abstractmethod
from typing import Dict, Optional, List, Protocol, Callable, Any
from abs_integration_core.schema import TokenData, Integration
from datetime import datetime, timedelta, UTC
import httpx


class IntegrationServiceProtocol(Protocol):
    """Protocol defining the interface for integration services"""
    
    def get_auth_url(self, state: Optional[Dict] = None) -> Dict[str, str]:
        """
        Generate an authentication URL for OAuth flow.
        
        Args:
            state: Optional state dictionary to include in the OAuth flow
        
        Returns:
            A dictionary containing the auth URL and other necessary information
        """
        ...

    async def handle_oauth_callback(self, code: str) -> TokenData:
        """
        Handle the OAuth callback and store tokens.
        
        Args:
            code: The authorization code from OAuth callback
            
        Returns:
            TokenData object
        """
        ...

    def get_query_by_provider(self):
        """Get the integration query by provider"""
        ...

    def get_all_integrations(self) -> List[Integration]:
        """
        Get all integrations.
        
        Returns:
            List of TokenData objects
        """
        ...

    async def refresh_token(self, token_url: str, refresh_data: Dict) -> Optional[TokenData]:
        """
        Refresh the access token using the refresh token.
        
        Returns:
            Updated TokenData if successful, None otherwise
        """
        ...

    async def get_integration(self) -> Optional[TokenData]:
        """
        Get integration data.
        
        Returns:
            TokenData if integration exists, None otherwise
        """
        ...

    async def delete_integration(self) -> bool:
        """
        Delete an integration.
        
        Returns:
            True if deleted, False otherwise
        """
        ...

    async def get_resource_subscription_method(self, resource_type: str) -> Callable:
        """
        Get the subscription method for a resource type.
        """
        ...

    async def subscribe(
        self,
        resource_type: str,
        site_id: str,
        resource_id: str,
        change_type: str = "created,updated,deleted",
        expiration_days: int = 3
    ) -> Dict:
        """
        Subscribe to a resource.
        """
        ...

    async def create_subscription(
        self,
        resource: str,
        change_type: str = "created,updated,deleted",
        expiration_days: int = 3,
    ) -> Dict:
        """
        Create a subscription for a resource.
        """
        ...

    async def renew_subscription(self, subscription_id: str, expiration_days: int = 3) -> Dict:
        """
        Renew a subscription.
        """
        ...
    
    async def delete_subscription(self, subscription_id: str) -> None:
        """
        Delete a subscription.
        """
        ...
    
    async def list_subscriptions(self) -> List[Dict]:
        """
        List all subscriptions.
        """
        ...

    async def handle_subscription_notification(self, notification_data: Dict) -> None:
        """
        Handle a subscription notification.
        """
        ...
    
    async def get_resource_path(
        self,
        resource_type: str,
        site_id: str,
        resource_id: str
    ) -> str:
        """
        Get the resource path for a SharePoint resource.
        """
        ...

    async def list_resources(self) -> List[Dict[str, Any]]:
        """
        List all resources.
        """
        ...


class AbstractIntegrationBaseService(IntegrationServiceProtocol):
    """
    Base abstract class for all integration services.
    Any integration service should inherit from this class and implement its methods.
    """
    async def refresh_integration_token(self) -> TokenData:
        """
        Refresh the access token using the refresh token.
        
        Returns:
            Updated TokenData if successful, None otherwise
        """
        refresh_data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "scope": self.scopes,
        }
        return await self.refresh_token(self.token_url, refresh_data)

    async def get_integration_token_data(self, code: str) -> TokenData:
        """
        Exchange authorization code for token data.
        
        Args:
            code: The authorization code from OAuth callback
            
        Returns:
            TokenData object with access_token, refresh_token and expires_in
        """
        token_data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_url,
            "grant_type": "authorization_code",
            "scope": self.scopes,
        }

        return await self.get_token_data(self.token_url, token_data)

    async def get_token_data(self, token_url: str, token_data: Dict) -> TokenData:
        """
        Exchange authorization code for token data.
        
        Args:
            code: The authorization code from OAuth callback
            
        Returns:
            TokenData object with access_token, refresh_token and expires_in
        """
        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=token_data)
            token_response.raise_for_status()
            token = token_response.json()

        expires_in = token.get("expires_in", 3600)
        expires_at = datetime.now(
        ) + timedelta(seconds=expires_in)
    
        return TokenData(
            access_token=token.get("access_token"),
            refresh_token=token.get("refresh_token"),
            expires_at=expires_at
        )

    async def _verify_access_token(self, token_data: TokenData) -> TokenData:
        """
        Verify the access token and refresh it if it's close to expiration.
        
        Args:
            token_data: The token data to verify
        
        Returns:
            TokenData object - either the original if valid or a refreshed one
        """
        current_time = datetime.now(UTC)
        buffer_minutes = 5
        expiration_buffer = current_time + timedelta(minutes=buffer_minutes)
        
        # Ensure token_data.expires_at is also timezone-aware
        if token_data.expires_at.tzinfo is None:
            token_data.expires_at = token_data.expires_at.replace(tzinfo=UTC)

        if token_data.expires_at <= expiration_buffer:
            return await self.refresh_integration_token()
        
        return token_data

    async def get_integration_tokens(self) -> TokenData:
        """
        Get the integration tokens.
        """
        result = await self.get_query_by_provider()

        access_token = result.get("access_token") if isinstance(result, dict) else result.access_token
        refresh_token = result.get("refresh_token") if isinstance(result, dict) else result.refresh_token
        expires_at = result.get("expires_at") if isinstance(result, dict) else result.expires_at

        tokens = TokenData(
            access_token=self.encryption.decrypt_token(access_token),
            refresh_token=self.encryption.decrypt_token(refresh_token),
            expires_at=expires_at
        )

        return await self._verify_access_token(tokens)

