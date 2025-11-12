"""
Pydantic models for Gun Del Sol API

All request/response schemas used across the application
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# ============================================================================
# Token Models
# ============================================================================


class Token(BaseModel):
    id: int
    token_address: str
    token_name: Optional[str]
    token_symbol: Optional[str]
    acronym: str
    analysis_timestamp: str
    first_buy_timestamp: Optional[str]
    wallets_found: int
    credits_used: Optional[int] = None
    last_analysis_credits: Optional[int] = None
    wallet_addresses: Optional[List[str]] = None
    deleted_at: Optional[str] = None


class TokensResponse(BaseModel):
    total: int
    total_wallets: int
    tokens: List[Dict[str, Any]]


# ============================================================================
# Wallet Models
# ============================================================================


class MultiTokenWallet(BaseModel):
    wallet_address: str
    token_count: int
    token_names: List[str]
    token_addresses: List[str]
    token_ids: List[int]
    wallet_balance_usd: Optional[float]


class MultiTokenWalletsResponse(BaseModel):
    total: int
    wallets: List[Dict[str, Any]]


class WalletTag(BaseModel):
    tag: str
    is_kol: bool


class RefreshBalancesRequest(BaseModel):
    wallet_addresses: List[str] = Field(..., min_items=1)


class RefreshBalancesResponse(BaseModel):
    message: str
    results: List[Dict[str, Any]]
    total_wallets: int
    successful: int
    api_credits_used: int


# ============================================================================
# Tag Models
# ============================================================================


class AddTagRequest(BaseModel):
    tag: str
    is_kol: bool = False


class RemoveTagRequest(BaseModel):
    tag: str


class BatchTagsRequest(BaseModel):
    addresses: List[str]


class WalletTagRequest(BaseModel):
    tag: str
    is_kol: Optional[bool] = False


# ============================================================================
# Analysis Models
# ============================================================================


class AnalysisSettings(BaseModel):
    """API settings for token analysis"""

    transactionLimit: int = Field(default=500, ge=1, le=10000)
    minUsdFilter: float = Field(default=50.0, ge=0)
    walletCount: int = Field(default=10, ge=1, le=100)
    apiRateDelay: int = Field(default=100, ge=0)
    maxCreditsPerAnalysis: int = Field(default=1000, ge=1, le=10000)
    maxRetries: int = Field(default=3, ge=0, le=10)


class AnalyzeTokenRequest(BaseModel):
    """Request model for token analysis"""

    address: str = Field(..., min_length=32, max_length=44, description="Solana token address")
    api_settings: Optional[AnalysisSettings] = None
    min_usd: Optional[float] = None
    time_window_hours: int = Field(default=999999, ge=1)


class AnalysisJob(BaseModel):
    """Analysis job status"""

    job_id: str
    token_address: str
    status: str  # queued, processing, completed, failed
    created_at: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    axiom_file: Optional[str] = None
    result_file: Optional[str] = None


# ============================================================================
# Watchlist/Address Monitoring Models
# ============================================================================


class RegisterAddressRequest(BaseModel):
    address: str = Field(..., min_length=32, max_length=44)
    note: Optional[str] = None
    timestamp: Optional[str] = None


class AddressNoteRequest(BaseModel):
    note: Optional[str] = None


class ImportAddressEntry(BaseModel):
    address: str
    registered_at: Optional[str] = None
    threshold: Optional[int] = None
    total_notifications: Optional[int] = None
    last_notification: Optional[str] = None
    note: Optional[str] = None


class ImportAddressesRequest(BaseModel):
    addresses: List[ImportAddressEntry]


# ============================================================================
# Settings Models
# ============================================================================


class UpdateSettingsRequest(BaseModel):
    transactionLimit: Optional[int] = Field(None, ge=1, le=10000)
    minUsdFilter: Optional[float] = Field(None, ge=0)
    walletCount: Optional[int] = Field(None, ge=1, le=100)
    apiRateDelay: Optional[int] = Field(None, ge=0)
    maxCreditsPerAnalysis: Optional[int] = Field(None, ge=1, le=10000)
    maxRetries: Optional[int] = Field(None, ge=0, le=10)


# ============================================================================
# Webhook Models
# ============================================================================


class CreateWebhookRequest(BaseModel):
    token_id: int
    webhook_url: Optional[str] = None


# ============================================================================
# Notification Models
# ============================================================================


class AnalysisCompleteNotification(BaseModel):
    """Notification payload for analysis completion"""

    job_id: str
    token_name: str
    token_symbol: str
    acronym: str
    wallets_found: int
    token_id: int


class AnalysisStartNotification(BaseModel):
    """Notification payload for analysis start"""

    job_id: str
    token_name: str
    token_symbol: str
