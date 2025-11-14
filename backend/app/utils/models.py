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


class Wallet(BaseModel):
    id: int
    wallet_address: str
    first_buy_timestamp: str
    total_usd: Optional[float]
    transaction_count: Optional[int]
    average_buy_usd: Optional[float]
    wallet_balance_usd: Optional[float]


class TokenDetail(BaseModel):
    """Token with wallet details and axiom data"""

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
    deleted_at: Optional[str] = None
    wallets: List[Wallet]
    axiom_json: List[Any]


class TokensResponse(BaseModel):
    total: int
    total_wallets: int
    tokens: List[Token]


class MessageResponse(BaseModel):
    """Simple message response"""

    message: str


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
    wallets: List[MultiTokenWallet]


class WalletTag(BaseModel):
    tag: str
    is_kol: bool


class RefreshBalancesRequest(BaseModel):
    wallet_addresses: List[str] = Field(..., min_items=1)


class RefreshBalancesResult(BaseModel):
    wallet_address: str
    balance_usd: Optional[float]
    success: bool


class RefreshBalancesResponse(BaseModel):
    message: str
    results: List[RefreshBalancesResult]
    total_wallets: int
    successful: int
    api_credits_used: int


# ============================================================================
# Tag Models
# ============================================================================


class WalletTagsResponse(BaseModel):
    tags: List[WalletTag]


class TagsResponse(BaseModel):
    tags: List[str]


class CodexWallet(BaseModel):
    wallet_address: str
    tags: List[WalletTag]


class CodexResponse(BaseModel):
    wallets: List[CodexWallet]


# ============================================================================
# Analysis History Models
# ============================================================================


class AnalysisRun(BaseModel):
    id: int
    analysis_timestamp: str
    wallets_found: int
    credits_used: int
    wallets: List[Wallet]


class AnalysisHistory(BaseModel):
    token_id: int
    total_runs: int
    runs: List[AnalysisRun]


# ============================================================================
# Original Tag Models (keeping for compatibility)
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
