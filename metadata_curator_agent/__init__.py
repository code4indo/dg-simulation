"""
Metadata Curator Agent Package

AI Agent untuk Manajemen Metadata Arsip dengan Human-in-the-Loop
menggunakan Google Gemini AI dan Streamlit.
"""

__version__ = "1.0.0"
__author__ = "Data Governance Team"
__email__ = "dg-team@domain.com"
__description__ = "AI Agent untuk Manajemen Metadata Arsip"

from .metadata_curator_agent import MetadataCuratorAgent
from .database import MetadataDatabase
from .utils import DocumentProcessor, MetadataValidator, QualityMetrics

__all__ = [
    "MetadataCuratorAgent",
    "MetadataDatabase", 
    "DocumentProcessor",
    "MetadataValidator",
    "QualityMetrics"
]
