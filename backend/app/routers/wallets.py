"""
Wallets router - multi-token wallets and balance refresh endpoints

Provides REST endpoints for wallet operations
"""

import asyncio

import aiosqlite
import requests
from fastapi import APIRouter, HTTPException

from app import settings
from app.cache import ResponseCache
from app.utils.models import (
    MultiTokenWalletsResponse,
    RefreshBalancesRequest,
    RefreshBalancesResponse,
)

router = APIRouter()
cache = ResponseCache()


@router.get("/multi-token-wallets", response_model=MultiTokenWalletsResponse)
async def get_multi_early_buyer_wallets(min_tokens: int = 2):
    """Get wallets that appear in multiple tokens"""
    cache_key = f"multi_early_buyer_wallets_{min_tokens}"
    cached_data, _ = cache.get(cache_key)
    if cached_data:
        return cached_data

    async with aiosqlite.connect(settings.DATABASE_FILE) as conn:
        conn.row_factory = aiosqlite.Row
        query = """
            SELECT
                tw.wallet_address,
                COUNT(DISTINCT tw.token_id) as token_count,
                GROUP_CONCAT(DISTINCT t.token_name) as token_names,
                GROUP_CONCAT(DISTINCT t.token_address) as token_addresses,
                GROUP_CONCAT(DISTINCT t.id) as token_ids,
                MAX(tw.wallet_balance_usd) as wallet_balance_usd
            FROM early_buyer_wallets tw
            JOIN analyzed_tokens t ON tw.token_id = t.id
            WHERE t.deleted_at IS NULL
            GROUP BY tw.wallet_address
            HAVING COUNT(DISTINCT tw.token_id) >= ?
            ORDER BY token_count DESC, wallet_balance_usd DESC
        """
        cursor = await conn.execute(query, (min_tokens,))
        rows = await cursor.fetchall()

        wallets = []
        for row in rows:
            wallet_dict = dict(row)
            wallet_dict["token_names"] = wallet_dict["token_names"].split(",") if wallet_dict["token_names"] else []
            wallet_dict["token_addresses"] = (
                wallet_dict["token_addresses"].split(",") if wallet_dict["token_addresses"] else []
            )
            wallet_dict["token_ids"] = [
                int(id) for id in wallet_dict["token_ids"].split(",") if wallet_dict["token_ids"]
            ]
            wallets.append(wallet_dict)

        result = {"total": len(wallets), "wallets": wallets}
        cache.set(cache_key, result)
        return result


@router.post("/wallets/refresh-balances", response_model=RefreshBalancesResponse)
async def refresh_wallet_balances(request: RefreshBalancesRequest):
    """Refresh wallet balances for multiple wallets (ASYNC)"""
    wallet_addresses = request.wallet_addresses
    api_key = settings.HELIUS_API_KEY

    if not api_key:
        raise HTTPException(status_code=500, detail="Helius API key not configured")

    async def fetch_balance(wallet_address: str):
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(
                    f"https://api.helius.xyz/v0/addresses/{wallet_address}/balances?api-key={api_key}", timeout=10
                ),
            )

            if response.status_code == 200:
                data = response.json()
                balance_usd = data.get("nativeBalance", 0) * 0.001
                return {"wallet_address": wallet_address, "balance_usd": balance_usd, "success": True}
            else:
                return {"wallet_address": wallet_address, "balance_usd": None, "success": False}
        except Exception:
            return {"wallet_address": wallet_address, "balance_usd": None, "success": False}

    # Fetch all balances concurrently
    results = await asyncio.gather(*[fetch_balance(addr) for addr in wallet_addresses])

    # Update database
    async with aiosqlite.connect(settings.DATABASE_FILE) as conn:
        for result in results:
            if result["success"] and result["balance_usd"] is not None:
                await conn.execute(
                    "UPDATE early_buyer_wallets SET wallet_balance_usd = ? WHERE wallet_address = ?",
                    (result["balance_usd"], result["wallet_address"]),
                )
        await conn.commit()

    cache.invalidate("multi_early_buyer_wallets")

    successful = sum(1 for r in results if r["success"])

    return {
        "message": f"Refreshed {successful} of {len(wallet_addresses)} wallets",
        "results": results,
        "total_wallets": len(wallet_addresses),
        "successful": successful,
        "api_credits_used": len(wallet_addresses),
    }
