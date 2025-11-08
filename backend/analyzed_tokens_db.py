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
import os
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import contextmanager

# Use absolute path to ensure database is always in the backend directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_FILE = os.path.join(SCRIPT_DIR, 'analyzed_tokens.db')


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
                webhook_id TEXT,
                credits_used INTEGER DEFAULT 0,
                last_analysis_credits INTEGER DEFAULT 0
            )
        ''')

        # Analysis runs table - tracks each time we analyze a token
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_id INTEGER NOT NULL,
                analysis_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                wallets_found INTEGER DEFAULT 0,
                credits_used INTEGER DEFAULT 0,
                FOREIGN KEY (token_id) REFERENCES analyzed_tokens(id) ON DELETE CASCADE
            )
        ''')

        # Early buyer wallets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS early_buyer_wallets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_id INTEGER NOT NULL,
                analysis_run_id INTEGER NOT NULL,
                wallet_address TEXT NOT NULL,
                position INTEGER NOT NULL,
                first_buy_usd REAL,
                total_usd REAL,
                transaction_count INTEGER,
                average_buy_usd REAL,
                first_buy_timestamp TIMESTAMP,
                axiom_name TEXT,
                FOREIGN KEY (token_id) REFERENCES analyzed_tokens(id) ON DELETE CASCADE,
                FOREIGN KEY (analysis_run_id) REFERENCES analysis_runs(id) ON DELETE CASCADE,
                UNIQUE(analysis_run_id, wallet_address)
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

        # Wallet tags table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wallet_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wallet_address TEXT NOT NULL,
                tag TEXT NOT NULL,
                is_kol BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(wallet_address, tag)
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

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_wallet_tags_address
            ON wallet_tags(wallet_address)
        ''')

        # Run migrations to add new columns to existing tables
        # Check if total_usd column exists in early_buyer_wallets, if not add it
        cursor.execute("PRAGMA table_info(early_buyer_wallets)")
        ebw_columns = [col[1] for col in cursor.fetchall()]

        if 'total_usd' not in ebw_columns:
            print("[Database] Migrating: Adding total_usd column...")
            cursor.execute('ALTER TABLE early_buyer_wallets ADD COLUMN total_usd REAL')

        if 'transaction_count' not in ebw_columns:
            print("[Database] Migrating: Adding transaction_count column...")
            cursor.execute('ALTER TABLE early_buyer_wallets ADD COLUMN transaction_count INTEGER')

        if 'average_buy_usd' not in ebw_columns:
            print("[Database] Migrating: Adding average_buy_usd column...")
            cursor.execute('ALTER TABLE early_buyer_wallets ADD COLUMN average_buy_usd REAL')

        # Check if credits_used and last_analysis_credits columns exist in analyzed_tokens, if not add them
        cursor.execute("PRAGMA table_info(analyzed_tokens)")
        at_columns = [col[1] for col in cursor.fetchall()]

        if 'credits_used' not in at_columns:
            print("[Database] Migrating: Adding credits_used column...")
            cursor.execute('ALTER TABLE analyzed_tokens ADD COLUMN credits_used INTEGER DEFAULT 0')

        if 'last_analysis_credits' not in at_columns:
            print("[Database] Migrating: Adding last_analysis_credits column...")
            cursor.execute('ALTER TABLE analyzed_tokens ADD COLUMN last_analysis_credits INTEGER DEFAULT 0')

        # Migration for analysis_run_id column in early_buyer_wallets
        if 'analysis_run_id' not in ebw_columns:
            print("[Database] Migrating: Adding analysis_run_id column to early_buyer_wallets...")
            print("[Database] Warning: Existing wallet records will be linked to a default analysis run")

            # Add the column (allowing NULL temporarily for migration)
            cursor.execute('ALTER TABLE early_buyer_wallets ADD COLUMN analysis_run_id INTEGER')

            # For each existing token, create an analysis_run entry
            cursor.execute('SELECT DISTINCT token_id FROM early_buyer_wallets WHERE analysis_run_id IS NULL')
            token_ids = cursor.fetchall()

            for row in token_ids:
                token_id = row[0]
                # Get the token's analysis timestamp
                cursor.execute('SELECT analysis_timestamp, wallets_found, last_analysis_credits FROM analyzed_tokens WHERE id = ?', (token_id,))
                token_data = cursor.fetchone()

                if token_data:
                    analysis_timestamp, wallets_found, credits = token_data[0], token_data[1], token_data[2]

                    # Create an analysis run for this token
                    cursor.execute('''
                        INSERT INTO analysis_runs (token_id, analysis_timestamp, wallets_found, credits_used)
                        VALUES (?, ?, ?, ?)
                    ''', (token_id, analysis_timestamp, wallets_found or 0, credits or 0))

                    analysis_run_id = cursor.lastrowid

                    # Link all existing wallets for this token to this analysis run
                    cursor.execute('''
                        UPDATE early_buyer_wallets
                        SET analysis_run_id = ?
                        WHERE token_id = ? AND analysis_run_id IS NULL
                    ''', (analysis_run_id, token_id))

            print("[Database] Migration complete: Existing wallets linked to analysis runs")

        # Migration for is_kol column in wallet_tags
        cursor.execute("PRAGMA table_info(wallet_tags)")
        wt_columns = [col[1] for col in cursor.fetchall()]

        if 'is_kol' not in wt_columns:
            print("[Database] Migrating: Adding is_kol column to wallet_tags...")
            cursor.execute('ALTER TABLE wallet_tags ADD COLUMN is_kol BOOLEAN DEFAULT 0')

        print("[Database] Schema initialized successfully")


def save_analyzed_token(
    token_address: str,
    token_name: str,
    token_symbol: str,
    acronym: str,
    early_bidders: List[Dict],
    axiom_json: List[Dict],
    first_buy_timestamp: Optional[str] = None,
    credits_used: int = 0
) -> int:
    """
    Save analyzed token and its early buyers.

    Args:
        token_address: Solana token mint address
        token_name: Token name
        token_symbol: Token symbol
        acronym: Generated acronym
        early_bidders: List of early buyer wallet data
        axiom_json: Axiom wallet tracker export JSON
        first_buy_timestamp: Timestamp of first buy transaction
        credits_used: Helius API credits used for this analysis

    Returns:
        token_id: Database ID of the saved token
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Insert or update analyzed token
        cursor.execute('''
            INSERT INTO analyzed_tokens (
                token_address, token_name, token_symbol, acronym,
                first_buy_timestamp, wallets_found, axiom_json, credits_used, last_analysis_credits
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(token_address) DO UPDATE SET
                token_name = excluded.token_name,
                token_symbol = excluded.token_symbol,
                acronym = excluded.acronym,
                analysis_timestamp = CURRENT_TIMESTAMP,
                first_buy_timestamp = excluded.first_buy_timestamp,
                wallets_found = excluded.wallets_found,
                axiom_json = excluded.axiom_json,
                credits_used = analyzed_tokens.credits_used + excluded.credits_used,
                last_analysis_credits = excluded.last_analysis_credits
        ''', (
            token_address,
            token_name,
            token_symbol,
            acronym,
            first_buy_timestamp,
            len(early_bidders),
            json.dumps(axiom_json),
            credits_used,
            credits_used
        ))

        # Get the token ID
        cursor.execute('SELECT id FROM analyzed_tokens WHERE token_address = ?', (token_address,))
        token_id = cursor.fetchone()['id']

        # Create a new analysis run entry for this analysis
        cursor.execute('''
            INSERT INTO analysis_runs (token_id, wallets_found, credits_used)
            VALUES (?, ?, ?)
        ''', (token_id, len(early_bidders), credits_used))

        analysis_run_id = cursor.lastrowid
        print(f"[Database] Created analysis run #{analysis_run_id} for token {acronym}")

        # Insert early buyer wallets linked to this analysis run
        # NOTE: We do NOT delete existing wallets - we keep all historical analyses
        for index, bidder in enumerate(early_bidders[:10], start=1):
            total_usd = bidder.get('total_usd', 0)
            first_buy_usd = round(total_usd)
            transaction_count = bidder.get('transaction_count', 1)
            average_buy_usd = bidder.get('average_buy_usd', total_usd)
            axiom_name = f"({index}/10)${first_buy_usd}|{acronym}"

            cursor.execute('''
                INSERT INTO early_buyer_wallets (
                    token_id, analysis_run_id, wallet_address, position, first_buy_usd,
                    total_usd, transaction_count, average_buy_usd,
                    first_buy_timestamp, axiom_name
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                token_id,
                analysis_run_id,
                bidder['wallet_address'],
                index,
                first_buy_usd,
                total_usd,
                transaction_count,
                average_buy_usd,
                bidder.get('first_buy_time'),
                axiom_name
            ))

        print(f"[Database] Saved token {acronym} with {len(early_bidders[:10])} wallets (run #{analysis_run_id})")
        return token_id


def get_analyzed_tokens(limit: int = 50) -> List[Dict]:
    """Get list of analyzed tokens, most recent first"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT
                id, token_address, token_name, token_symbol, acronym,
                analysis_timestamp, first_buy_timestamp, wallets_found, credits_used, last_analysis_credits
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

        # Get associated wallets from the most recent analysis run
        cursor.execute('''
            SELECT ebw.* FROM early_buyer_wallets ebw
            JOIN analysis_runs ar ON ebw.analysis_run_id = ar.id
            WHERE ebw.token_id = ?
            ORDER BY ar.analysis_timestamp DESC, ebw.position ASC
            LIMIT 10
        ''', (token_id,))

        token_dict['wallets'] = [dict(row) for row in cursor.fetchall()]

        return token_dict


def get_token_analysis_history(token_id: int) -> List[Dict]:
    """
    Get all analysis runs for a token, most recent first.
    Each run includes its wallets.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Get all analysis runs for this token
        cursor.execute('''
            SELECT id, analysis_timestamp, wallets_found, credits_used
            FROM analysis_runs
            WHERE token_id = ?
            ORDER BY analysis_timestamp DESC
        ''', (token_id,))

        runs = []
        for run_row in cursor.fetchall():
            run_dict = dict(run_row)

            # Get wallets for this specific run
            cursor.execute('''
                SELECT * FROM early_buyer_wallets
                WHERE analysis_run_id = ?
                ORDER BY position ASC
            ''', (run_dict['id'],))

            run_dict['wallets'] = [dict(w) for w in cursor.fetchall()]
            runs.append(run_dict)

        return runs


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


def search_tokens(query: str) -> List[Dict]:
    """
    Search tokens by token address, token name, symbol, acronym, or wallet address.
    Returns list of tokens that match the search (case-insensitive).
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        search_pattern = f'%{query}%'

        # Search by token fields OR tokens that have matching wallets
        cursor.execute('''
            SELECT DISTINCT
                at.id, at.token_address, at.token_name, at.token_symbol, at.acronym,
                at.analysis_timestamp, at.first_buy_timestamp, at.wallets_found,
                at.credits_used, at.last_analysis_credits
            FROM analyzed_tokens at
            WHERE at.token_address LIKE ? COLLATE NOCASE
               OR at.token_name LIKE ? COLLATE NOCASE
               OR at.token_symbol LIKE ? COLLATE NOCASE
               OR at.acronym LIKE ? COLLATE NOCASE
               OR at.id IN (
                   SELECT DISTINCT token_id
                   FROM early_buyer_wallets
                   WHERE wallet_address LIKE ? COLLATE NOCASE
               )
            ORDER BY at.analysis_timestamp DESC
        ''', (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))

        tokens = []
        for row in cursor.fetchall():
            tokens.append(dict(row))

        return tokens


def get_multi_token_wallets(min_tokens: int = 2) -> List[Dict]:
    """
    Find wallets that appear in multiple analyzed tokens.
    Returns list of wallets with their token appearances.

    Args:
        min_tokens: Minimum number of tokens a wallet must appear in (default: 2)

    Returns:
        List of dicts with wallet_address, token_count, and list of tokens
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Find wallets that appear in multiple tokens
        cursor.execute('''
            SELECT
                ebw.wallet_address,
                COUNT(DISTINCT ebw.token_id) as token_count,
                GROUP_CONCAT(DISTINCT at.token_name || ' (' || at.token_symbol || ')') as token_names,
                GROUP_CONCAT(DISTINCT at.token_address) as token_addresses,
                GROUP_CONCAT(DISTINCT ebw.token_id) as token_ids
            FROM early_buyer_wallets ebw
            JOIN analyzed_tokens at ON ebw.token_id = at.id
            GROUP BY ebw.wallet_address
            HAVING COUNT(DISTINCT ebw.token_id) >= ?
            ORDER BY token_count DESC, ebw.wallet_address
        ''', (min_tokens,))

        wallets = []
        for row in cursor.fetchall():
            wallets.append({
                'wallet_address': row[0],
                'token_count': row[1],
                'token_names': row[2].split(',') if row[2] else [],
                'token_addresses': row[3].split(',') if row[3] else [],
                'token_ids': [int(x) for x in row[4].split(',')] if row[4] else []
            })

        return wallets


def add_wallet_tag(wallet_address: str, tag: str, is_kol: bool = False) -> bool:
    """
    Add a tag to a wallet address.

    Args:
        wallet_address: The wallet address to tag
        tag: The tag to add
        is_kol: Whether this is a KOL (Key Opinion Leader) tag

    Returns:
        True if tag was added, False if it already existed
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO wallet_tags (wallet_address, tag, is_kol)
                VALUES (?, ?, ?)
            ''', (wallet_address, tag, 1 if is_kol else 0))
            return True
        except sqlite3.IntegrityError:
            # Tag already exists for this wallet
            return False


def remove_wallet_tag(wallet_address: str, tag: str) -> bool:
    """
    Remove a tag from a wallet address.

    Args:
        wallet_address: The wallet address
        tag: The tag to remove

    Returns:
        True if tag was removed, False if it didn't exist
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM wallet_tags
            WHERE wallet_address = ? AND tag = ?
        ''', (wallet_address, tag))
        return cursor.rowcount > 0


def get_wallet_tags(wallet_address: str) -> List[Dict]:
    """
    Get all tags for a wallet address.

    Args:
        wallet_address: The wallet address

    Returns:
        List of tag dictionaries with 'tag' and 'is_kol' fields
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT tag, is_kol FROM wallet_tags
            WHERE wallet_address = ?
            ORDER BY created_at DESC
        ''', (wallet_address,))
        return [{'tag': row[0], 'is_kol': bool(row[1])} for row in cursor.fetchall()]


def get_all_tags() -> List[str]:
    """
    Get all unique tags across all wallets.

    Returns:
        List of unique tag strings
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT tag FROM wallet_tags
            ORDER BY tag
        ''')
        return [row[0] for row in cursor.fetchall()]


def get_wallets_by_tag(tag: str) -> List[str]:
    """
    Get all wallet addresses with a specific tag.

    Args:
        tag: The tag to search for

    Returns:
        List of wallet addresses
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT wallet_address FROM wallet_tags
            WHERE tag = ?
            ORDER BY created_at DESC
        ''', (tag,))
        return [row[0] for row in cursor.fetchall()]


# Initialize database on module import
init_database()