"""
Test configuration untuk metadata curator agent
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import Mock, MagicMock

# Test fixtures
@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_text():
    """Sample text untuk testing ekstraksi metadata"""
    return """
    Laporan Tahunan Keuangan 2023
    
    Departemen Keuangan Republik Indonesia
    
    Laporan ini berisi ringkasan kinerja keuangan tahun 2023.
    Disusun oleh Tim Analisis Keuangan pada tanggal 31 Desember 2023.
    
    Bahasa: Indonesia
    Klasifikasi: Publik
    """

@pytest.fixture
def sample_metadata():
    """Sample metadata untuk testing"""
    return {
        "dublin_core": {
            "title": "Laporan Tahunan Keuangan 2023",
            "creator": "Departemen Keuangan",
            "subject": "Keuangan, Laporan Tahunan",
            "description": "Laporan kinerja keuangan tahun 2023",
            "date": "2023-12-31",
            "type": "Laporan",
            "language": "id",
            "rights": "Publik"
        },
        "isad_g": {
            "title": "Laporan Tahunan Keuangan 2023",
            "date": "2023-12-31",
            "name_of_creator": "Departemen Keuangan",
            "scope_and_content": "Laporan kinerja keuangan"
        },
        "confidence_score": 0.85
    }

@pytest.fixture
def mock_gemini_response():
    """Mock response dari Gemini AI"""
    mock_response = Mock()
    mock_response.text = """{
        "dublin_core": {
            "title": "Test Document",
            "creator": "Test Author",
            "date": "2023-01-01",
            "type": "Document"
        },
        "isad_g": {
            "title": "Test Document",
            "date": "2023-01-01"
        },
        "confidence_score": 0.8
    }"""
    return mock_response

@pytest.fixture
def mock_db():
    """Mock database untuk testing"""
    db = Mock()
    db.save_metadata.return_value = 1
    db.get_statistics.return_value = {
        "total_records": 5,
        "average_confidence": 0.85,
        "average_completeness": 0.75,
        "schema_distribution": {"dublin_core": 3, "isad_g": 2},
        "validation_distribution": {"Setuju": 4, "Perlu perbaikan": 1}
    }
    return db
