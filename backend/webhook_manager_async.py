"""
Async Webhook Manager for Helius API
Uses httpx for non-blocking HTTP operations
"""

import httpx
from typing import List, Dict, Optional


class AsyncWebhookManager:
    """Async webhook manager using httpx for non-blocking operations"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.webhook_url = "https://api.helius.xyz/v0/webhooks"

    async def create_webhook(
        self,
        webhook_url: str,
        wallet_addresses: List[str],
        webhook_type: str = "enhanced",
        transaction_types: Optional[List[str]] = None
    ) -> Dict:
        """
        Create a new Helius webhook (async)

        Args:
            webhook_url: Server endpoint for webhook notifications
            wallet_addresses: Wallet addresses to monitor
            webhook_type: "enhanced" or "raw"
            transaction_types: Transaction types to monitor

        Returns:
            Webhook creation response with webhook_id
        """
        if transaction_types is None:
            transaction_types = ["TRANSFER", "SWAP", "NFT_SALE", "TOKEN_MINT"]

        payload = {
            "webhookURL": webhook_url,
            "transactionTypes": transaction_types,
            "accountAddresses": wallet_addresses,
            "webhookType": webhook_type
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.webhook_url}?api-key={self.api_key}",
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                print(f"[Webhook] Created webhook {result.get('webhookID')} for {len(wallet_addresses)} addresses")
                return result
        except Exception as e:
            raise Exception(f"Failed to create webhook: {str(e)}")

    async def update_webhook(
        self,
        webhook_id: str,
        wallet_addresses: Optional[List[str]] = None,
        webhook_url: Optional[str] = None,
        transaction_types: Optional[List[str]] = None
    ) -> Dict:
        """Update existing webhook (async)"""
        payload = {}
        if wallet_addresses is not None:
            payload["accountAddresses"] = wallet_addresses
        if webhook_url is not None:
            payload["webhookURL"] = webhook_url
        if transaction_types is not None:
            payload["transactionTypes"] = transaction_types

        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{self.webhook_url}/{webhook_id}?api-key={self.api_key}",
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                print(f"[Webhook] Updated webhook {webhook_id}")
                return result
        except Exception as e:
            raise Exception(f"Failed to update webhook: {str(e)}")

    async def delete_webhook(self, webhook_id: str) -> bool:
        """Delete webhook (async)"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.webhook_url}/{webhook_id}?api-key={self.api_key}",
                    timeout=30.0
                )
                response.raise_for_status()
                print(f"[Webhook] Deleted webhook {webhook_id}")
                return True
        except Exception as e:
            raise Exception(f"Failed to delete webhook: {str(e)}")

    async def get_webhook(self, webhook_id: str) -> Dict:
        """Get webhook details (async)"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.webhook_url}/{webhook_id}?api-key={self.api_key}",
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            raise Exception(f"Failed to get webhook: {str(e)}")

    async def list_webhooks(self) -> List[Dict]:
        """List all webhooks (async)"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.webhook_url}?api-key={self.api_key}",
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            raise Exception(f"Failed to list webhooks: {str(e)}")
