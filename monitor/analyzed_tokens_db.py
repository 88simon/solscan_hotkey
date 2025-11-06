"""
============================================================================
Database Module - SENSITIVE DATA STORAGE
============================================================================
This module stores analyzed tokens and wallet activity in SQLite.

⚠️  SECURITY WARNING - CONTAINS SENSITIVE TRADING DATA  ⚠️

The database file (analyzed_tokens.db) contains:
- Wallet addresses of early buyers you discovered
- Token analysis results revealing your research
- Trading strategies and patterns

This data should NEVER be committed to version control or shared publicly.
The database files are protected by .gitignore.

============================================================================
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import contextmanager

DATABASE_FILE = 'analyzed_tokens.db'


@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def init_database():
    """Initialize database schema"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Analyzed tokens table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analyzed_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_address TEXT UNIQUE NOT NULL,
                token_name TEXT,
                token_symbol TEXT,
                acronym TEXT,
                analysis_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                first_buy_timestamp TIMESTAMP,
                wallets_found INTEGER DEFAULT 0,
                axiom_json TEXT,
                webhook_id TEXT
            )
        ''')

        # Early buyer wallets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS early_buyer_wallets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_id INTEGER NOT NULL,
                wallet_address TEXT NOT NULL,
                position INTEGER NOT NULL,
                first_buy_usd REAL,
                total_usd REAL,
                transaction_count INTEGER,
                average_buy_usd REAL,
                first_buy_timestamp TIMESTAMP,
                axiom_name TEXT,
                FOREIGN KEY (token_id) REFERENCES analyzed_tokens(id) ON DELETE CASCADE,
                UNIQUE(token_id, wallet_address)
            )
        ''')

        # Wallet activity events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wallet_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wallet_id INTEGER NOT NULL,
                transaction_signature TEXT UNIQUE,
                timestamp TIMESTAMP,
                activity_type TEXT,
                description TEXT,
                sol_amount REAL,
                token_amount REAL,
                recipient_address TEXT,
                FOREIGN KEY (wallet_id) REFERENCES early_buyer_wallets(id) ON DELETE CASCADE
            )
        ''')

        # Create indices for better query performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_token_address
            ON analyzed_tokens(token_address)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_wallet_address
            ON early_buyer_wallets(wallet_address)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_activity_timestamp
            ON wallet_activity(timestamp DESC)
        ''')

        # Run migrations to add new columns to existing tables
        # Check if total_usd column exists, if not add it
        cursor.execute("PRAGMA table_info(early_buyer_wallets)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'total_usd' not in columns:
            print("[Database] Migrating: Adding total_usd column...")
            cursor.execute('ALTER TABLE early_buyer_wallets ADD COLUMN total_usd REAL')

        if 'transaction_count' not in columns:
            print("[Database] Migrating: Adding transaction_count column...")
            cursor.execute('ALTER TABLE early_buyer_wallets ADD COLUMN transaction_count INTEGER')

        if 'average_buy_usd' not in columns:
            print("[Database] Migrating: Adding average_buy_usd column...")
            cursor.execute('ALTER TABLE early_buyer_wallets ADD COLUMN average_buy_usd REAL')

        print("[Database] Schema initialized successfully")


def save_analyzed_token(
    token_address: str,
    token_name: str,
    token_symbol: str,
    acronym: str,
    early_bidders: List[Dict],
    axiom_json: List[Dict],
    first_buy_timestamp: Optional[str] = None
) -> int:
    """
    Save analyzed token and its early buyers.

    Returns:
        token_id: Database ID of the saved token
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Insert or update analyzed token
        cursor.execute('''
            INSERT INTO analyzed_tokens (
                token_address, token_name, token_symbol, acronym,
                first_buy_timestamp, wallets_found, axiom_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(token_address) DO UPDATE SET
                token_name = excluded.token_name,
                token_symbol = excluded.token_symbol,
                acronym = excluded.acronym,
                analysis_timestamp = CURRENT_TIMESTAMP,
                first_buy_timestamp = excluded.first_buy_timestamp,
                wallets_found = excluded.wallets_found,
                axiom_json = excluded.axiom_json
        ''', (
            token_address,
            token_name,
            token_symbol,
            acronym,
            first_buy_timestamp,
            len(early_bidders),
            json.dumps(axiom_json)
        ))

        # Get the token ID
        cursor.execute('SELECT id FROM analyzed_tokens WHERE token_address = ?', (token_address,))
        token_id = cursor.fetchone()['id']

        # Delete existing wallets for this token (in case of re-analysis)
        cursor.execute('DELETE FROM early_buyer_wallets WHERE token_id = ?', (token_id,))

        # Insert early buyer wallets
        for index, bidder in enumerate(early_bidders[:10], start=1):
            total_usd = bidder.get('total_usd', 0)
            first_buy_usd = round(total_usd)
            transaction_count = bidder.get('transaction_count', 1)
            average_buy_usd = bidder.get('average_buy_usd', total_usd)
            axiom_name = f"({index}/10)${first_buy_usd}|{acronym}"

            cursor.execute('''
                INSERT INTO early_buyer_wallets (
                    token_id, wallet_address, position, first_buy_usd,
                    total_usd, transaction_count, average_buy_usd,
                    first_buy_timestamp, axiom_name
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                token_id,
                bidder['wallet_address'],
                index,
                first_buy_usd,
                total_usd,
                transaction_count,
                average_buy_usd,
                bidder.get('first_buy_time'),
                axiom_name
            ))

        print(f"[Database] Saved token {acronym} with {len(early_bidders[:10])} wallets")
        return token_id


def get_analyzed_tokens(limit: int = 50) -> List[Dict]:
    """Get list of analyzed tokens, most recent first"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT
                id, token_address, token_name, token_symbol, acronym,
                analysis_timestamp, first_buy_timestamp, wallets_found
            FROM analyzed_tokens
            ORDER BY analysis_timestamp DESC
            LIMIT ?
        ''', (limit,))

        tokens = []
        for row in cursor.fetchall():
            tokens.append(dict(row))

        return tokens


def get_token_details(token_id: int) -> Optional[Dict]:
    """Get detailed information about a specific analyzed token"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Get token info
        cursor.execute('''
            SELECT * FROM analyzed_tokens WHERE id = ?
        ''', (token_id,))

        token = cursor.fetchone()
        if not token:
            return None

        token_dict = dict(token)

        # Parse axiom_json back to list
        if token_dict.get('axiom_json'):
            token_dict['axiom_json'] = json.loads(token_dict['axiom_json'])

        # Get associated wallets
        cursor.execute('''
            SELECT * FROM early_buyer_wallets
            WHERE token_id = ?
            ORDER BY position ASC
        ''', (token_id,))

        token_dict['wallets'] = [dict(row) for row in cursor.fetchall()]

        return token_dict


def get_wallet_activity(wallet_id: int, limit: int = 50) -> List[Dict]:
    """Get activity history for a specific wallet"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM wallet_activity
            WHERE wallet_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (wallet_id, limit))

        return [dict(row) for row in cursor.fetchall()]


def save_wallet_activity(
    wallet_address: str,
    transaction_signature: str,
    timestamp: str,
    activity_type: str,
    description: str,
    sol_amount: float = 0.0,
    token_amount: float = 0.0,
    recipient_address: str = None
) -> bool:
    """Save a wallet activity event"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Find wallet_id
        cursor.execute('''
            SELECT id FROM early_buyer_wallets
            WHERE wallet_address = ?
            LIMIT 1
        ''', (wallet_address,))

        wallet = cursor.fetchone()
        if not wallet:
            return False  # Wallet not being tracked

        wallet_id = wallet['id']

        # Insert activity (ignore duplicates)
        try:
            cursor.execute('''
                INSERT INTO wallet_activity (
                    wallet_id, transaction_signature, timestamp,
                    activity_type, description, sol_amount,
                    token_amount, recipient_address
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                wallet_id, transaction_signature, timestamp,
                activity_type, description, sol_amount,
                token_amount, recipient_address
            ))
            return True
        except sqlite3.IntegrityError:
            # Duplicate transaction signature
            return False


def get_recent_activity(limit: int = 100) -> List[Dict]:
    """Get recent wallet activity across all tracked wallets"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT
                wa.*,
                ebw.wallet_address,
                ebw.axiom_name,
                at.token_name,
                at.acronym
            FROM wallet_activity wa
            JOIN early_buyer_wallets ebw ON wa.wallet_id = ebw.id
            JOIN analyzed_tokens at ON ebw.token_id = at.id
            ORDER BY wa.timestamp DESC
            LIMIT ?
        ''', (limit,))

        return [dict(row) for row in cursor.fetchall()]


def delete_analyzed_token(token_id: int) -> bool:
    """
    Delete an analyzed token and all associated data.

    This will CASCADE delete:
    - The token record from analyzed_tokens
    - All associated wallets from early_buyer_wallets
    - All wallet activity from wallet_activity

    Args:
        token_id: Database ID of the token to delete

    Returns:
        True if deleted successfully, False if token not found
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Check if token exists
        cursor.execute('SELECT id FROM analyzed_tokens WHERE id = ?', (token_id,))
        if not cursor.fetchone():
            return False

        # Delete token (CASCADE will delete wallets and activity)
        cursor.execute('DELETE FROM analyzed_tokens WHERE id = ?', (token_id,))

        print(f"[Database] Deleted token ID {token_id} and all associated data")
        return True


# Initialize database on module import
init_database()