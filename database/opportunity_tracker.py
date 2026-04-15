"""
⚔️ OPPORTUNITY TRACKER
База данных возможностей с AI-анализом
"""
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

DB_PATH = Path(__file__).parent.parent / 'data' / 'opportunities.db'
DB_PATH.parent.mkdir(exist_ok=True)

class OpportunityTracker:
    """Трекер возможностей"""
    
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self._init_db()
    
    def _init_db(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                source TEXT,
                potential REAL,
                risk INTEGER,
                status TEXT DEFAULT 'new',
                score INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS hunts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                opportunity_id INTEGER,
                hunter_id TEXT,
                status TEXT,
                earnings REAL,
                started_at TIMESTAMP,
                finished_at TIMESTAMP,
                FOREIGN KEY(opportunity_id) REFERENCES opportunities(id)
            )
        ''')
        self.conn.commit()
    
    def add_opportunity(self, title: str, description: str, source: str, 
                       potential: float, risk: int, score: int) -> int:
        cursor = self.conn.execute('''
            INSERT INTO opportunities (title, description, source, potential, risk, score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, description, source, potential, risk, score))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_opportunities(self, status: str = None, limit: int = 10) -> List[Dict]:
        query = 'SELECT * FROM opportunities'
        params = []
        if status:
            query += ' WHERE status = ?'
            params.append(status)
        query += ' ORDER BY score DESC LIMIT ?'
        params.append(limit)
        
        cursor = self.conn.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def update_status(self, opp_id: int, status: str):
        self.conn.execute('''
            UPDATE opportunities 
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, opp_id))
        self.conn.commit()
    
    def start_hunt(self, opp_id: int, hunter_id: str) -> int:
        cursor = self.conn.execute('''
            INSERT INTO hunts (opportunity_id, hunter_id, status, started_at)
            VALUES (?, ?, 'active', CURRENT_TIMESTAMP)
        ''', (opp_id, hunter_id))
        self.conn.commit()
        return cursor.lastrowid
    
    def finish_hunt(self, hunt_id: int, earnings: float):
        self.conn.execute('''
            UPDATE hunts 
            SET status = 'completed', earnings = ?, finished_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (earnings, hunt_id))
        self.conn.commit()
    
    def get_stats(self) -> Dict:
        cursor = self.conn.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'new' THEN 1 ELSE 0 END) as new_count,
                SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_count,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_count
            FROM opportunities
        ''')
        opp_stats = dict(zip(['total', 'new', 'active', 'completed'], cursor.fetchone()))
        
        cursor = self.conn.execute('SELECT SUM(earnings) as total FROM hunts')
        earnings = cursor.fetchone()[0] or 0
        
        return {
            **opp_stats,
            'total_earnings': earnings
        }
    
    def close(self):
        self.conn.close()


__all__ = ['OpportunityTracker']
