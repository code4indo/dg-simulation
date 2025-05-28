import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Any
import os

class MetadataDatabase:
    """Database manager untuk menyimpan metadata dan hasil validasi"""
    
    def __init__(self, db_path: str = "metadata.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table untuk metadata records
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metadata_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT,
                schema_type TEXT,
                dublin_core TEXT,
                isad_g TEXT,
                confidence_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table untuk validation results
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS validation_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metadata_id INTEGER,
                is_valid BOOLEAN,
                completeness_score REAL,
                missing_fields TEXT,
                invalid_fields TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (metadata_id) REFERENCES metadata_records (id)
            )
        ''')
        
        # Table untuk human feedback
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS human_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metadata_id INTEGER,
                validation_status TEXT,
                feedback TEXT,
                user_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (metadata_id) REFERENCES metadata_records (id)
            )
        ''')
        
        # Table untuk inconsistency reports
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inconsistency_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_type TEXT,
                issues TEXT,
                metadata_ids TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_metadata(self, file_name: str, metadata: Dict[str, Any], schema_type: str) -> int:
        """Simpan metadata ke database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        dublin_core_json = json.dumps(metadata.get("dublin_core", {}))
        isad_g_json = json.dumps(metadata.get("isad_g", {}))
        confidence_score = metadata.get("confidence_score", 0.0)
        
        cursor.execute('''
            INSERT INTO metadata_records (file_name, schema_type, dublin_core, isad_g, confidence_score)
            VALUES (?, ?, ?, ?, ?)
        ''', (file_name, schema_type, dublin_core_json, isad_g_json, confidence_score))
        
        metadata_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return metadata_id
    
    def save_validation_result(self, metadata_id: int, validation_results: Dict[str, Any]):
        """Simpan hasil validasi"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO validation_results (metadata_id, is_valid, completeness_score, missing_fields, invalid_fields)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            metadata_id,
            validation_results["is_valid"],
            validation_results["completeness_score"],
            json.dumps(validation_results["missing_fields"]),
            json.dumps(validation_results["invalid_fields"])
        ))
        
        conn.commit()
        conn.close()
    
    def save_human_feedback(self, metadata_id: int, validation_status: str, feedback: str, user_id: str = "user"):
        """Simpan feedback manual dari human validator"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO human_feedback (metadata_id, validation_status, feedback, user_id)
            VALUES (?, ?, ?, ?)
        ''', (metadata_id, validation_status, feedback, user_id))
        
        conn.commit()
        conn.close()
    
    def get_metadata_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Ambil riwayat metadata yang sudah diproses"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT mr.*, vr.is_valid, vr.completeness_score, hf.validation_status, hf.feedback
            FROM metadata_records mr
            LEFT JOIN validation_results vr ON mr.id = vr.metadata_id
            LEFT JOIN human_feedback hf ON mr.id = hf.metadata_id
            ORDER BY mr.created_at DESC
            LIMIT ?
        ''', (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append(dict(row))
        
        conn.close()
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Ambil statistik database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total records
        cursor.execute("SELECT COUNT(*) FROM metadata_records")
        total_records = cursor.fetchone()[0]
        
        # Average confidence score
        cursor.execute("SELECT AVG(confidence_score) FROM metadata_records")
        avg_confidence = cursor.fetchone()[0] or 0.0
        
        # Average completeness score
        cursor.execute("SELECT AVG(completeness_score) FROM validation_results")
        avg_completeness = cursor.fetchone()[0] or 0.0
        
        # Records by schema type
        cursor.execute("SELECT schema_type, COUNT(*) FROM metadata_records GROUP BY schema_type")
        schema_distribution = dict(cursor.fetchall())
        
        # Validation status distribution
        cursor.execute("SELECT validation_status, COUNT(*) FROM human_feedback GROUP BY validation_status")
        validation_distribution = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            "total_records": total_records,
            "average_confidence": round(avg_confidence, 3),
            "average_completeness": round(avg_completeness, 3),
            "schema_distribution": schema_distribution,
            "validation_distribution": validation_distribution
        }
