try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import docx
except ImportError:
    docx = None

from typing import Dict, Any, Optional, List
import io
import mimetypes

class DocumentProcessor:
    """Processor untuk berbagai format dokumen"""
    
    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> str:
        """Ekstrak teks dari file PDF"""
        if PyPDF2 is None:
            return "PyPDF2 not installed. Please install with: pip install PyPDF2"
        
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            return f"Error reading PDF: {str(e)}"
    
    @staticmethod
    def extract_text_from_docx(file_content: bytes) -> str:
        """Ekstrak teks dari file DOCX"""
        if docx is None:
            return "python-docx not installed. Please install with: pip install python-docx"
        
        try:
            doc = docx.Document(io.BytesIO(file_content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            return f"Error reading DOCX: {str(e)}"
    
    @staticmethod
    def extract_text_from_txt(file_content: bytes, encoding: str = "utf-8") -> str:
        """Ekstrak teks dari file TXT"""
        try:
            return file_content.decode(encoding)
        except UnicodeDecodeError:
            try:
                return file_content.decode("latin-1")
            except Exception as e:
                return f"Error reading TXT: {str(e)}"
    
    @classmethod
    def process_file(cls, file_content: bytes, file_name: str, mime_type: str) -> str:
        """Process file berdasarkan tipe dan ekstrak teks"""
        if mime_type == "application/pdf":
            return cls.extract_text_from_pdf(file_content)
        elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return cls.extract_text_from_docx(file_content)
        elif mime_type == "text/plain":
            return cls.extract_text_from_txt(file_content)
        else:
            # Fallback: coba deteksi dari extension
            extension = file_name.lower().split('.')[-1] if '.' in file_name else ''
            if extension == 'pdf':
                return cls.extract_text_from_pdf(file_content)
            elif extension in ['docx', 'doc']:
                return cls.extract_text_from_docx(file_content)
            elif extension == 'txt':
                return cls.extract_text_from_txt(file_content)
            else:
                return f"Unsupported file type: {mime_type}"

class MetadataValidator:
    """Advanced metadata validation with custom rules"""
    
    @staticmethod
    def validate_date_format(date_string: str) -> Dict[str, Any]:
        """Validasi format tanggal yang lebih detail"""
        import re
        from datetime import datetime
        
        validation_result = {
            "is_valid": False,
            "format": "unknown",
            "standardized": "",
            "errors": []
        }
        
        # Pattern untuk berbagai format tanggal
        patterns = {
            "ISO": r"^\d{4}-\d{2}-\d{2}$",
            "DD/MM/YYYY": r"^\d{2}/\d{2}/\d{4}$",
            "MM/DD/YYYY": r"^\d{2}/\d{2}/\d{4}$",
            "YYYY": r"^\d{4}$",
            "DD-MM-YYYY": r"^\d{2}-\d{2}-\d{4}$"
        }
        
        for format_name, pattern in patterns.items():
            if re.match(pattern, date_string.strip()):
                validation_result["format"] = format_name
                validation_result["is_valid"] = True
                
                # Coba standardisasi ke format ISO
                try:
                    if format_name == "ISO":
                        validation_result["standardized"] = date_string
                    elif format_name == "DD/MM/YYYY":
                        dt = datetime.strptime(date_string, "%d/%m/%Y")
                        validation_result["standardized"] = dt.strftime("%Y-%m-%d")
                    elif format_name == "YYYY":
                        validation_result["standardized"] = f"{date_string}-01-01"
                    # Add more format conversions as needed
                except ValueError as e:
                    validation_result["errors"].append(f"Invalid date: {str(e)}")
                    validation_result["is_valid"] = False
                
                break
        
        if not validation_result["is_valid"]:
            validation_result["errors"].append("Date format not recognized")
        
        return validation_result
    
    @staticmethod
    def validate_language_code(language: str) -> Dict[str, Any]:
        """Validasi kode bahasa"""
        # ISO 639-1 language codes (sample)
        valid_languages = {
            "id": "Indonesian",
            "en": "English",
            "ms": "Malay",
            "zh": "Chinese",
            "ar": "Arabic",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "ja": "Japanese",
            "ko": "Korean"
        }
        
        language_lower = language.lower().strip()
        
        return {
            "is_valid": language_lower in valid_languages,
            "language_name": valid_languages.get(language_lower, "Unknown"),
            "suggestion": "Use ISO 639-1 language codes (e.g., 'id' for Indonesian, 'en' for English)"
        }
    
    @staticmethod
    def validate_creator_format(creator: str) -> Dict[str, Any]:
        """Validasi format creator/author"""
        validation_result = {
            "is_valid": True,
            "suggestions": [],
            "standardized": creator.strip()
        }
        
        # Check for common issues
        if not creator.strip():
            validation_result["is_valid"] = False
            validation_result["suggestions"].append("Creator field cannot be empty")
            return validation_result
        
        # Check for inconsistent formatting
        if creator.lower() == creator:
            validation_result["suggestions"].append("Consider proper capitalization for names")
        
        if len(creator.split()) == 1 and not creator.isupper():
            validation_result["suggestions"].append("Consider adding full name or organization")
        
        # Check for organization vs individual
        org_indicators = ["dept", "department", "ministry", "agency", "office", "bureau", "center", "institute"]
        if any(indicator in creator.lower() for indicator in org_indicators):
            validation_result["suggestions"].append("Detected organization - ensure consistent naming")
        
        return validation_result

class QualityMetrics:
    """Menghitung berbagai metrik kualitas metadata"""
    
    @staticmethod
    def calculate_completeness_score(metadata: Dict[str, Any], schema_fields: Dict[str, str]) -> float:
        """Hitung skor kelengkapan metadata"""
        filled_fields = 0
        total_fields = len(schema_fields)
        
        for field in schema_fields.keys():
            if metadata.get(field) and str(metadata[field]).strip():
                filled_fields += 1
        
        return filled_fields / total_fields if total_fields > 0 else 0.0
    
    @staticmethod
    def calculate_consistency_score(metadata_list: List[Dict[str, Any]]) -> Dict[str, float]:
        """Hitung skor konsistensi untuk batch metadata"""
        if len(metadata_list) < 2:
            return {"overall": 1.0}
        
        consistency_scores = {}
        
        # Check date format consistency
        date_formats = set()
        for metadata in metadata_list:
            date_val = metadata.get("date", "")
            if date_val:
                validator = MetadataValidator()
                result = validator.validate_date_format(date_val)
                date_formats.add(result["format"])
        
        consistency_scores["date_format"] = 1.0 if len(date_formats) <= 1 else 0.5
        
        # Check language consistency
        languages = set()
        for metadata in metadata_list:
            lang = metadata.get("language", "").lower()
            if lang:
                languages.add(lang)
        
        consistency_scores["language"] = 1.0 if len(languages) <= 1 else 0.7
        
        # Overall consistency score
        consistency_scores["overall"] = sum(consistency_scores.values()) / len(consistency_scores)
        
        return consistency_scores
    
    @staticmethod
    def calculate_richness_score(metadata: Dict[str, Any]) -> float:
        """Hitung skor kekayaan/detail metadata"""
        richness_indicators = {
            "description_length": len(str(metadata.get("description", ""))),
            "has_subject": bool(metadata.get("subject", "")),
            "has_coverage": bool(metadata.get("coverage", "")),
            "has_relation": bool(metadata.get("relation", "")),
            "has_rights": bool(metadata.get("rights", ""))
        }
        
        score = 0.0
        
        # Description length score (0-0.3)
        desc_length = richness_indicators["description_length"]
        if desc_length > 200:
            score += 0.3
        elif desc_length > 100:
            score += 0.2
        elif desc_length > 50:
            score += 0.1
        
        # Optional fields score (0.7 total)
        optional_fields = ["has_subject", "has_coverage", "has_relation", "has_rights"]
        filled_optional = sum(1 for field in optional_fields if richness_indicators[field])
        score += (filled_optional / len(optional_fields)) * 0.7
        
        return min(score, 1.0)
