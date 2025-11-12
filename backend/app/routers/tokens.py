"""
Tokens router - token management endpoints

Provides REST endpoints for token history, details, trash management, and exports
"""

import json
from datetime import datetime

import aiosqlite
from fastapi import APIRouter, HTTPException, Request, Response

from app import settings
from app.cache import ResponseCache

router = APIRouter()
cache = ResponseCache()


@router.get("/api/tokens/history")
async def get_tokens_history(request: Request, response: Response):
    """Get all non-deleted tokens with wallet counts (with caching)"""
    cache_key = "tokens_history"

    # Check cache first
    cached_data, cached_etag = cache.get(cache_key)
    if cached_data:
        if_none_match = request.headers.get("if-none-match")
        if if_none_match and if_none_match == cached_etag:
            response.status_code = 304
            return Response(status_code=304)
        response.headers["ETag"] = cached_etag
        return cached_data

    # Fetch from database
    async def fetch_tokens():
        async with aiosqlite.connect(settings.DATABASE_FILE) as conn:
            conn.row_factory = aiosqlite.Row
            query = """
                SELECT
                    t.id, t.token_address, t.token_name, t.token_symbol, t.acronym,
                    t.analysis_timestamp, t.first_buy_timestamp,
                    COUNT(DISTINCT ebw.wallet_address) as wallets_found,
                    t.credits_used, t.last_analysis_credits
                FROM analyzed_tokens t
                LEFT JOIN early_buyer_wallets ebw ON ebw.token_id = t.id
                WHERE t.deleted_at IS NULL OR t.deleted_at = ''
                GROUP BY t.id
                ORDER BY t.analysis_timestamp DESC
            """
            cursor = await conn.execute(query)
            rows = await cursor.fetchall()

            tokens = []
            total_wallets = 0
            for row in rows:
                token_dict = dict(row)
                tokens.append(token_dict)
                total_wallets += token_dict.get("wallets_found", 0)

            return {"total": len(tokens), "total_wallets": total_wallets, "tokens": tokens}

    result = await cache.deduplicate_request(cache_key, fetch_tokens)
    etag = cache.set(cache_key, result)
    response.headers["ETag"] = etag
    return result


@router.get("/api/tokens/trash")
async def get_deleted_tokens():
    """Get all soft-deleted tokens"""
    async with aiosqlite.connect(settings.DATABASE_FILE) as conn:
        conn.row_factory = aiosqlite.Row
        query = """
            SELECT
                t.*, COUNT(DISTINCT ebw.wallet_address) as wallets_found
            FROM analyzed_tokens t
            LEFT JOIN early_buyer_wallets ebw ON ebw.token_id = t.id
            WHERE t.deleted_at IS NOT NULL
            GROUP BY t.id
            ORDER BY t.deleted_at DESC
        """
        cursor = await conn.execute(query)
        rows = await cursor.fetchall()

        tokens = [dict(row) for row in rows]
        return {"total": len(tokens), "total_wallets": sum(t.get("wallets_found", 0) for t in tokens), "tokens": tokens}


@router.get("/api/tokens/{token_id}")
async def get_token_by_id(token_id: int):
    """Get token details with wallets and axiom export"""
    async with aiosqlite.connect(settings.DATABASE_FILE) as conn:
        conn.row_factory = aiosqlite.Row

        # Get token info
        token_query = "SELECT * FROM analyzed_tokens WHERE id = ? AND deleted_at IS NULL"
        cursor = await conn.execute(token_query, (token_id,))
        token_row = await cursor.fetchone()

        if not token_row:
            raise HTTPException(status_code=404, detail="Token not found")

        token = dict(token_row)

        # Get wallets for this token
        wallets_query = """
            SELECT * FROM early_buyer_wallets
            WHERE token_id = ?
            ORDER BY first_buy_timestamp ASC
        """
        cursor = await conn.execute(wallets_query, (token_id,))
        wallet_rows = await cursor.fetchall()
        token["wallets"] = [dict(row) for row in wallet_rows]

        # Get axiom export
        axiom_query = "SELECT axiom_json FROM analyzed_tokens WHERE id = ?"
        cursor = await conn.execute(axiom_query, (token_id,))
        axiom_row = await cursor.fetchone()
        token["axiom_json"] = json.loads(axiom_row[0]) if axiom_row and axiom_row[0] else []

        return token


@router.get("/api/tokens/{token_id}/history")
async def get_token_analysis_history(token_id: int):
    """Get analysis history for a specific token"""
    async with aiosqlite.connect(settings.DATABASE_FILE) as conn:
        conn.row_factory = aiosqlite.Row

        # Verify token exists
        token_query = "SELECT id FROM analyzed_tokens WHERE id = ?"
        cursor = await conn.execute(token_query, (token_id,))
        if not await cursor.fetchone():
            raise HTTPException(status_code=404, detail="Token not found")

        # Fetch analysis runs
        runs_query = """
            SELECT id, analysis_timestamp, wallets_found, credits_used
            FROM analysis_runs
            WHERE token_id = ?
            ORDER BY analysis_timestamp DESC
        """
        cursor = await conn.execute(runs_query, (token_id,))
        run_rows = await cursor.fetchall()

        runs = []
        for run_row in run_rows:
            run = dict(run_row)
            wallets_query = """
                SELECT *
                FROM early_buyer_wallets
                WHERE analysis_run_id = ?
                ORDER BY position ASC
            """
            wallet_cursor = await conn.execute(wallets_query, (run["id"],))
            wallet_rows = await wallet_cursor.fetchall()
            run["wallets"] = [dict(w) for w in wallet_rows]
            runs.append(run)

        return {"token_id": token_id, "total_runs": len(runs), "runs": runs}


@router.delete("/api/tokens/{token_id}")
async def soft_delete_token(token_id: int):
    """Soft delete a token (move to trash)"""
    async with aiosqlite.connect(settings.DATABASE_FILE) as conn:
        query = "UPDATE analyzed_tokens SET deleted_at = ? WHERE id = ?"
        await conn.execute(query, (datetime.utcnow().isoformat(), token_id))
        await conn.commit()

    cache.invalidate("tokens")
    return {"message": "Token moved to trash"}


@router.post("/api/tokens/{token_id}/restore")
async def restore_token(token_id: int):
    """Restore a soft-deleted token"""
    async with aiosqlite.connect(settings.DATABASE_FILE) as conn:
        query = "UPDATE analyzed_tokens SET deleted_at = NULL WHERE id = ?"
        await conn.execute(query, (token_id,))
        await conn.commit()

    cache.invalidate("tokens")
    return {"message": "Token restored"}


@router.delete("/api/tokens/{token_id}/permanent")
async def permanent_delete_token(token_id: int):
    """Permanently delete a token and all associated data"""
    async with aiosqlite.connect(settings.DATABASE_FILE) as conn:
        # Delete in order: wallets, analysis runs, token
        await conn.execute("DELETE FROM early_buyer_wallets WHERE token_id = ?", (token_id,))
        await conn.execute("DELETE FROM analysis_runs WHERE token_id = ?", (token_id,))
        await conn.execute("DELETE FROM analyzed_tokens WHERE id = ?", (token_id,))
        await conn.commit()

    cache.invalidate("tokens")
    return {"message": "Token permanently deleted"}
