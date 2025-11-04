"""
Helius API Integration for Solana Token Analysis
Provides functions to analyze tokens and extract early bidder data
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import base58

class HeliusAPI:
    """Wrapper for Helius RPC and Enhanced API endpoints"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.rpc_url = f"https://mainnet.helius-rpc.com/?api-key={api_key}"
        self.enhanced_url = "https://api.helius.xyz/v0"
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})

    def _rpc_call(self, method: str, params: list) -> dict:
        """Make a JSON-RPC call to Helius"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }
        try:
            response = self.session.post(self.rpc_url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            if 'error' in result:
                raise Exception(f"RPC Error: {result['error']}")
            return result.get('result', {})
        except Exception as e:
            raise Exception(f"RPC call failed: {str(e)}")

    def _enhanced_call(self, endpoint: str, params: dict) -> dict:
        """Make a call to Helius Enhanced API"""
        url = f"{self.enhanced_url}/{endpoint}"
        params['api-key'] = self.api_key
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Enhanced API call failed: {str(e)}")

    def get_token_metadata(self, mint_address: str) -> Optional[Dict]:
        """Get token metadata including name, symbol, etc."""
        try:
            result = self._enhanced_call('token-metadata', {
                'mintAccounts': mint_address
            })
            return result[0] if result else None
        except Exception as e:
            print(f"Error fetching token metadata: {str(e)}")
            return None

    def get_parsed_transactions(self, address: str, limit: int = 100) -> List[Dict]:
        """
        Get parsed transaction history for an address.
        Returns transactions with decoded swap/transfer data.
        """
        try:
            # Get transaction signatures first
            signatures = self._rpc_call('getSignaturesForAddress', [
                address,
                {"limit": limit}
            ])

            if not signatures:
                return []

            # Get parsed transactions using Enhanced API
            sig_list = [sig['signature'] for sig in signatures[:limit]]

            result = self._enhanced_call('transactions', {
                'transactions': ','.join(sig_list)
            })

            return result if isinstance(result, list) else []

        except Exception as e:
            print(f"Error fetching parsed transactions: {str(e)}")
            return []

    def analyze_token_early_bidders(
        self,
        mint_address: str,
        min_usd: float = 50.0,
        time_window_hours: int = 24,
        max_transactions: int = 500
    ) -> Dict:
        """
        Analyze a token to find early bidders.

        Args:
            mint_address: Token mint address to analyze
            min_usd: Minimum USD amount to consider (default: $50)
            time_window_hours: Hours from first transaction to consider (default: 24)
            max_transactions: Maximum transactions to analyze (default: 500)

        Returns:
            Dictionary with analysis results:
            {
                'token_address': str,
                'token_info': dict,
                'first_transaction_time': datetime,
                'analysis_window_end': datetime,
                'early_bidders': [
                    {
                        'wallet_address': str,
                        'first_buy_time': datetime,
                        'total_usd': float,
                        'transaction_count': int,
                        'average_buy_usd': float
                    }
                ],
                'total_unique_buyers': int,
                'total_transactions_analyzed': int
            }
        """
        print(f"[Helius] Analyzing token: {mint_address}")

        # Get token metadata
        token_info = self.get_token_metadata(mint_address)
        print(f"[Helius] Token info: {token_info.get('onChainMetadata', {}).get('metadata', {}).get('name', 'Unknown') if token_info else 'Unknown'}")

        # Get transaction history
        print(f"[Helius] Fetching up to {max_transactions} transactions...")
        transactions = self.get_parsed_transactions(mint_address, limit=max_transactions)
        print(f"[Helius] Retrieved {len(transactions)} transactions")

        if not transactions:
            return {
                'token_address': mint_address,
                'token_info': token_info,
                'error': 'No transactions found',
                'early_bidders': [],
                'total_unique_buyers': 0,
                'total_transactions_analyzed': 0
            }

        # Find first transaction timestamp
        first_tx_time = None
        for tx in reversed(transactions):  # Oldest first
            if tx.get('timestamp'):
                first_tx_time = datetime.fromtimestamp(tx['timestamp'])
                break

        if not first_tx_time:
            return {
                'token_address': mint_address,
                'token_info': token_info,
                'error': 'Could not determine first transaction time',
                'early_bidders': [],
                'total_unique_buyers': 0,
                'total_transactions_analyzed': 0
            }

        window_end = first_tx_time + timedelta(hours=time_window_hours)
        print(f"[Helius] Analysis window: {first_tx_time} to {window_end}")

        # Track buyers within time window
        buyers = {}  # wallet_address -> {first_buy, total_usd, tx_count}

        for tx in transactions:
            if not tx.get('timestamp'):
                continue

            tx_time = datetime.fromtimestamp(tx['timestamp'])

            # Skip transactions outside time window
            if tx_time > window_end:
                continue

            # Parse transaction for swap/buy activity
            buyer_wallet, usd_amount = self._extract_buy_info(tx, mint_address)

            if buyer_wallet and usd_amount and usd_amount >= min_usd:
                if buyer_wallet not in buyers:
                    buyers[buyer_wallet] = {
                        'wallet_address': buyer_wallet,
                        'first_buy_time': tx_time,
                        'total_usd': 0.0,
                        'transaction_count': 0
                    }

                buyers[buyer_wallet]['total_usd'] += usd_amount
                buyers[buyer_wallet]['transaction_count'] += 1

                # Keep earliest buy time
                if tx_time < buyers[buyer_wallet]['first_buy_time']:
                    buyers[buyer_wallet]['first_buy_time'] = tx_time

        # Convert to sorted list (earliest buyers first)
        early_bidders = list(buyers.values())
        for bidder in early_bidders:
            bidder['average_buy_usd'] = bidder['total_usd'] / bidder['transaction_count']

        early_bidders.sort(key=lambda x: x['first_buy_time'])

        print(f"[Helius] Found {len(early_bidders)} early bidders (>${min_usd} USD)")

        return {
            'token_address': mint_address,
            'token_info': token_info,
            'first_transaction_time': first_tx_time.isoformat(),
            'analysis_window_end': window_end.isoformat(),
            'early_bidders': early_bidders,
            'total_unique_buyers': len(early_bidders),
            'total_transactions_analyzed': len(transactions)
        }

    def _extract_buy_info(self, tx: dict, mint_address: str) -> tuple:
        """
        Extract buyer wallet and USD amount from a parsed transaction.
        Returns: (wallet_address, usd_amount) or (None, None)
        """
        try:
            # Check if this is a swap transaction
            if tx.get('type') == 'SWAP':
                # Look for swaps involving this token
                native_transfers = tx.get('nativeTransfers', [])
                token_transfers = tx.get('tokenTransfers', [])

                # Find if someone bought this token (received the token)
                for transfer in token_transfers:
                    if transfer.get('mint') == mint_address:
                        # Someone received this token
                        buyer = transfer.get('toUserAccount')

                        # Try to get USD amount from native transfers or token amount
                        usd_amount = 0.0

                        # Check if there's a corresponding SOL transfer (approximate USD)
                        for native in native_transfers:
                            if native.get('fromUserAccount') == buyer:
                                # They sent SOL, approximate USD (1 SOL ≈ variable, use amount * multiplier)
                                sol_amount = native.get('amount', 0) / 1e9  # Convert lamports to SOL
                                # For now, we'll just use token amount as proxy
                                # In production, you'd fetch SOL price
                                usd_amount = sol_amount * 100  # Rough estimate, update with real price

                        # Alternative: use token amount if available
                        if usd_amount == 0 and transfer.get('tokenAmount'):
                            # Use token amount as fallback
                            usd_amount = float(transfer.get('tokenAmount', 0))

                        return (buyer, usd_amount)

            # Check for direct token transfers (might be initial distribution)
            elif tx.get('type') in ['TRANSFER', 'TOKEN_MINT']:
                token_transfers = tx.get('tokenTransfers', [])
                for transfer in token_transfers:
                    if transfer.get('mint') == mint_address:
                        receiver = transfer.get('toUserAccount')
                        amount = float(transfer.get('tokenAmount', 0))
                        return (receiver, amount)

        except Exception as e:
            # Silently skip parsing errors for individual transactions
            pass

        return (None, None)


class TokenAnalyzer:
    """High-level token analysis interface"""

    def __init__(self, api_key: str):
        self.helius = HeliusAPI(api_key)

    def analyze_token(
        self,
        mint_address: str,
        min_usd: float = 50.0,
        time_window_hours: int = 24
    ) -> Dict:
        """
        Analyze a token to find early bidders.

        Args:
            mint_address: Token mint address
            min_usd: Minimum USD threshold (default: $50)
            time_window_hours: Analysis window in hours (default: 24)

        Returns:
            Analysis results dictionary
        """
        return self.helius.analyze_token_early_bidders(
            mint_address=mint_address,
            min_usd=min_usd,
            time_window_hours=time_window_hours
        )