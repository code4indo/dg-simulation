import streamlit as st
import google.generativeai as genai
import pandas as pd
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
import io
import zipfile
import mimetypes
from pathlib import Path

# Import our custom modules
from database import MetadataDatabase
from utils import DocumentProcessor, MetadataValidator, QualityMetrics

# Konfigurasi halaman Streamlit
st.set_page_config(
    page_title="Metadata Curator Agent",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

class EnhancedMetadataCuratorAgent:
    def __init__(self, api_key: str):
        """Initialize Enhanced Metadata Curator Agent dengan Gemini AI"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.db = MetadataDatabase()
        self.doc_processor = DocumentProcessor()
        self.validator = MetadataValidator()
        self.quality_metrics = QualityMetrics()
        
        # Skema metadata standar
        self.dublin_core_schema = {
            "title": "Judul dokumen",
            "creator": "Pembuat/Penulis",
            "subject": "Subjek/Topik",
            "description": "Deskripsi konten",
            "publisher": "Penerbit",
            "contributor": "Kontributor",
            "date": "Tanggal pembuatan/publikasi",
            "type": "Jenis dokumen",
            "format": "Format file",
            "identifier": "Identifikator unik",
            "source": "Sumber asal",
            "language": "Bahasa",
            "relation": "Relasi dengan dokumen lain",
            "coverage": "Cakupan geografis/temporal",
            "rights": "Hak cipta/akses"
        }
        
        self.isad_g_schema = {
            "reference_code": "Kode referensi",
            "title": "Judul",
            "date": "Tanggal",
            "level_of_description": "Tingkat deskripsi",
            "extent_and_medium": "Jumlah dan media",
            "name_of_creator": "Nama pembuat",
            "scope_and_content": "Ruang lingkup dan isi",
            "conditions_of_access": "Kondisi akses",
            "conditions_of_reproduction": "Kondisi reproduksi",
            "language_of_material": "Bahasa materi",
            "physical_characteristics": "Karakteristik fisik",
            "finding_aids": "Alat bantu pencarian",
            "location_of_originals": "Lokasi asli",
            "availability_of_copies": "Ketersediaan salinan",
            "related_units": "Unit terkait",
            "publication_note": "Catatan publikasi",
            "notes": "Catatan umum"
        }

    def extract_metadata_from_text(self, content: str, file_name: str = "") -> Dict[str, Any]:
        """Ekstrak metadata dari konten teks menggunakan Gemini"""
        prompt = f"""
        Sebagai AI spesialis metadata arsip, analisis konten berikut dan ekstrak metadata yang relevan sesuai dengan standar Dublin Core dan ISAD(G).
        
        Nama file: {file_name}
        Konten:
        {content[:4000]}  # Increased limit
        
        Berikan output dalam format JSON dengan struktur berikut:
        {{
            "dublin_core": {{
                "title": "judul yang diekstrak dari konten",
                "creator": "pembuat/penulis yang teridentifikasi",
                "subject": "subjek/topik utama",
                "description": "ringkasan konten yang informatif",
                "publisher": "penerbit jika ada",
                "date": "tanggal dalam format YYYY-MM-DD jika ditemukan",
                "type": "jenis dokumen (laporan/surat/memo/dll)",
                "format": "format file berdasarkan nama file",
                "language": "kode bahasa (id/en/dll)",
                "rights": "informasi hak akses jika ada"
            }},
            "isad_g": {{
                "reference_code": "kode referensi jika ada",
                "title": "judul untuk arsip",
                "date": "tanggal pembuatan",
                "level_of_description": "tingkat deskripsi (file/series/fonds)",
                "name_of_creator": "nama pembuat arsip",
                "scope_and_content": "ruang lingkup dan isi dokumen",
                "language_of_material": "bahasa materi"
            }},
            "confidence_score": 0.85,
            "extraction_notes": ["catatan tentang kualitas ekstraksi"],
            "suggestions": ["saran perbaikan metadata"]
        }}
        
        Berikan confidence score 0-1 berdasarkan kejelasan konten dan kualitas ekstraksi.
        Sertakan notes tentang kesulitan ekstraksi dan saran untuk perbaikan.
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Clean response text to ensure valid JSON
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3].strip()
            elif response_text.startswith('```'):
                response_text = response_text[3:-3].strip()
            
            metadata = json.loads(response_text)
            
            # Calculate additional quality metrics
            dc_metadata = metadata.get("dublin_core", {})
            metadata["quality_metrics"] = {
                "completeness_score": self.quality_metrics.calculate_completeness_score(
                    dc_metadata, self.dublin_core_schema
                ),
                "richness_score": self.quality_metrics.calculate_richness_score(dc_metadata)
            }
            
            return metadata
        except Exception as e:
            st.error(f"Error dalam ekstraksi metadata: {str(e)}")
            return self._get_empty_metadata()

    def advanced_validation(self, metadata: Dict[str, Any], schema_type: str = "dublin_core") -> Dict[str, Any]:
        """Validasi metadata yang lebih canggih"""
        schema = self.dublin_core_schema if schema_type == "dublin_core" else self.isad_g_schema
        validation_results = {
            "is_valid": True,
            "missing_fields": [],
            "invalid_fields": [],
            "warnings": [],
            "field_validations": {},
            "completeness_score": 0.0,
            "recommendations": []
        }
        
        metadata_section = metadata.get(schema_type, {})
        
        # Enhanced field validation
        for field, description in schema.items():
            field_value = metadata_section.get(field, "")
            
            if not field_value or not str(field_value).strip():
                validation_results["missing_fields"].append(field)
                validation_results["field_validations"][field] = {
                    "status": "missing",
                    "message": f"Field {field} is required but empty"
                }
            else:
                # Specific field validations
                if field == "date":
                    date_validation = self.validator.validate_date_format(str(field_value))
                    validation_results["field_validations"][field] = date_validation
                    if not date_validation["is_valid"]:
                        validation_results["invalid_fields"].extend(date_validation["errors"])
                
                elif field == "language":
                    lang_validation = self.validator.validate_language_code(str(field_value))
                    validation_results["field_validations"][field] = lang_validation
                    if not lang_validation["is_valid"]:
                        validation_results["warnings"].append(
                            f"Language code '{field_value}' may not be standard. {lang_validation['suggestion']}"
                        )
                
                elif field == "creator":
                    creator_validation = self.validator.validate_creator_format(str(field_value))
                    validation_results["field_validations"][field] = creator_validation
                    validation_results["warnings"].extend(creator_validation["suggestions"])
                
                else:
                    validation_results["field_validations"][field] = {
                        "status": "valid",
                        "value": field_value
                    }
        
        # Calculate completeness score
        filled_fields = sum(1 for field in schema.keys() if metadata_section.get(field))
        validation_results["completeness_score"] = filled_fields / len(schema)
        
        # Generate recommendations
        if validation_results["completeness_score"] < 0.7:
            validation_results["recommendations"].append(
                "Consider filling more metadata fields to improve discoverability"
            )
        
        if validation_results["invalid_fields"]:
            validation_results["recommendations"].append(
                "Fix invalid field formats for better data quality"
            )
        
        # Set overall validity
        validation_results["is_valid"] = (
            len(validation_results["missing_fields"]) == 0 and 
            len(validation_results["invalid_fields"]) == 0
        )
        
        return validation_results

    def _get_empty_metadata(self) -> Dict[str, Any]:
        """Return empty metadata structure"""
        return {
            "dublin_core": {field: "" for field in self.dublin_core_schema.keys()},
            "isad_g": {field: "" for field in self.isad_g_schema.keys()},
            "confidence_score": 0.0,
            "suggestions": [],
            "quality_metrics": {
                "completeness_score": 0.0,
                "richness_score": 0.0
            }
        }

def main():
    st.title("🏛️ Enhanced Metadata Curator Agent")
    st.markdown("**AI Agent untuk Manajemen Metadata Arsip dengan Human-in-the-Loop**")
    
    # Sidebar untuk konfigurasi
    with st.sidebar:
        st.header("⚙️ Konfigurasi")
        
        # Input API Key Gemini
        api_key = st.text_input("Gemini API Key", type="password", help="Masukkan API Key Google Gemini")
        
        if not api_key:
            st.warning("Silakan masukkan Gemini API Key untuk melanjutkan")
            st.stop()
        
        # Pilih skema metadata
        schema_type = st.selectbox(
            "Skema Metadata",
            ["dublin_core", "isad_g"],
            format_func=lambda x: "Dublin Core" if x == "dublin_core" else "ISAD(G)"
        )
        
        st.markdown("---")
        st.markdown("### 📊 Statistik Database")
        
        # Initialize agent to get stats
        agent = EnhancedMetadataCuratorAgent(api_key)
        stats = agent.db.get_statistics()
        
        st.metric("Total Records", stats["total_records"])
        st.metric("Avg Confidence", f"{stats['average_confidence']:.3f}")
        st.metric("Avg Completeness", f"{stats['average_completeness']:.3f}")

    # Main interface tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📄 Ekstraksi Metadata", 
        "✅ Validasi Lanjutan", 
        "🔍 Batch Analysis", 
        "🔗 Linked Data", 
        "📊 Dashboard",
        "📋 Riwayat"
    ])

    with tab1:
        st.header("Ekstraksi Metadata dengan AI")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Input method selection
            input_method = st.radio(
                "Pilih metode input:",
                ["Upload File", "Input Teks Manual"],
                horizontal=True
            )
            
            if input_method == "Upload File":
                uploaded_file = st.file_uploader(
                    "Upload dokumen arsip",
                    type=['txt', 'pdf', 'doc', 'docx', 'json'],
                    help="Format yang didukung: TXT, PDF, DOC, DOCX, JSON"
                )
                
                if uploaded_file is not None:
                    # Process file based on type
                    content = agent.doc_processor.process_file(
                        uploaded_file.read(),
                        uploaded_file.name,
                        uploaded_file.type
                    )
                    
                    with st.expander("Preview Konten", expanded=False):
                        st.text_area("", content[:1000] + "..." if len(content) > 1000 else content, height=200)
                    
                    if st.button("🤖 Ekstrak Metadata", type="primary"):
                        with st.spinner("Menganalisis dokumen dengan AI..."):
                            metadata = agent.extract_metadata_from_text(content, uploaded_file.name)
                            
                            # Save to database
                            metadata_id = agent.db.save_metadata(uploaded_file.name, metadata, schema_type)
                            
                            st.session_state.current_metadata = metadata
                            st.session_state.current_metadata_id = metadata_id
                        
                        st.success("✅ Metadata berhasil diekstrak dan disimpan!")

            else:  # Manual text input
                manual_text = st.text_area(
                    "Masukkan teks dokumen:",
                    height=200,
                    placeholder="Paste konten dokumen arsip di sini..."
                )
                
                file_name = st.text_input("Nama file (opsional):")
                
                if manual_text and st.button("🤖 Ekstrak Metadata", type="primary"):
                    with st.spinner("Menganalisis teks dengan AI..."):
                        metadata = agent.extract_metadata_from_text(manual_text, file_name)
                        
                        # Save to database
                        metadata_id = agent.db.save_metadata(file_name or "manual_input", metadata, schema_type)
                        
                        st.session_state.current_metadata = metadata
                        st.session_state.current_metadata_id = metadata_id
                    
                    st.success("✅ Metadata berhasil diekstrak dan disimpan!")

        with col2:
            if "current_metadata" in st.session_state:
                metadata = st.session_state.current_metadata
                
                # AI Quality Metrics
                st.subheader("🎯 Metrik Kualitas AI")
                
                confidence = metadata.get("confidence_score", 0.0)
                completeness = metadata.get("quality_metrics", {}).get("completeness_score", 0.0)
                richness = metadata.get("quality_metrics", {}).get("richness_score", 0.0)
                
                st.metric("Confidence Score", f"{confidence:.3f}")
                st.metric("Completeness", f"{completeness:.3f}")
                st.metric("Richness", f"{richness:.3f}")
                
                # Overall quality assessment
                overall_quality = (confidence + completeness + richness) / 3
                if overall_quality >= 0.8:
                    st.success("🟢 Kualitas Tinggi")
                elif overall_quality >= 0.6:
                    st.warning("🟡 Kualitas Sedang")
                else:
                    st.error("🔴 Perlu Perbaikan")

        # Display extracted metadata
        if "current_metadata" in st.session_state:
            metadata = st.session_state.current_metadata
            
            st.markdown("---")
            st.subheader("📋 Hasil Ekstraksi Metadata")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🏷️ Dublin Core**")
                dc_metadata = metadata.get("dublin_core", {})
                for field, value in dc_metadata.items():
                    st.text_input(
                        f"{field.replace('_', ' ').title()}", 
                        value, 
                        key=f"dc_{field}",
                        help=agent.dublin_core_schema.get(field, "")
                    )
            
            with col2:
                st.markdown("**📚 ISAD(G)**")
                isad_metadata = metadata.get("isad_g", {})
                for field, value in list(isad_metadata.items())[:8]:  # Show first 8 fields
                    st.text_input(
                        f"{field.replace('_', ' ').title()}", 
                        value, 
                        key=f"isad_{field}",
                        help=agent.isad_g_schema.get(field, "")
                    )
            
            # AI Insights
            if metadata.get("suggestions"):
                st.subheader("💡 Saran AI untuk Perbaikan")
                for i, suggestion in enumerate(metadata["suggestions"][:5], 1):
                    st.info(f"{i}. {suggestion}")

    with tab2:
        st.header("Validasi Metadata Lanjutan")
        
        if "current_metadata" in st.session_state:
            metadata = st.session_state.current_metadata
            
            # Enhanced validation
            validation_results = agent.advanced_validation(metadata, schema_type)
            
            # Save validation results
            if "current_metadata_id" in st.session_state:
                agent.db.save_validation_result(
                    st.session_state.current_metadata_id, 
                    validation_results
                )
            
            # Display validation dashboard
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                status = "✅ Valid" if validation_results["is_valid"] else "❌ Invalid"
                st.metric("Status Validasi", status)
            
            with col2:
                st.metric("Skor Kelengkapan", f"{validation_results['completeness_score']:.3f}")
            
            with col3:
                missing_count = len(validation_results["missing_fields"])
                st.metric("Field Hilang", missing_count)
            
            with col4:
                warning_count = len(validation_results["warnings"])
                st.metric("Peringatan", warning_count)
            
            # Detailed validation results
            if validation_results["missing_fields"]:
                st.subheader("⚠️ Field yang Hilang")
                for field in validation_results["missing_fields"]:
                    st.warning(f"Field '{field}' tidak ada atau kosong")
            
            if validation_results["invalid_fields"]:
                st.subheader("❌ Field yang Tidak Valid")
                for field in validation_results["invalid_fields"]:
                    st.error(field)
            
            # Detailed field validations
            with st.expander("🔍 Detail Validasi Per Field", expanded=False):
                for field, validation in validation_results["field_validations"].items():
                    if validation["status"] == "missing":
                        st.error(f"**{field}**: {validation['message']}")
                    elif validation["status"] == "valid":
                        st.success(f"**{field}**: Valid")
                    else:
                        st.warning(f"**{field}**: Perlu review")
            
            # Human-in-the-loop validation
            st.markdown("---")
            st.subheader("👤 Validasi Manual (Human-in-the-Loop)")
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                human_validation = st.radio(
                    "Status validasi Anda:",
                    ["Belum ditentukan", "Setuju", "Perlu perbaikan", "Tolak"],
                    help="Berikan penilaian manual terhadap hasil AI"
                )
            
            with col2:
                feedback = st.text_area(
                    "Feedback dan komentar:",
                    placeholder="Berikan feedback detail untuk meningkatkan akurasi AI...",
                    height=100
                )
            
            if human_validation != "Belum ditentukan":
                if st.button("💾 Simpan Validasi Manual", type="primary"):
                    # Save human feedback
                    if "current_metadata_id" in st.session_state:
                        agent.db.save_human_feedback(
                            st.session_state.current_metadata_id,
                            human_validation,
                            feedback
                        )
                    
                    st.success(f"✅ Validasi disimpan: {human_validation}")
                    if feedback:
                        st.info(f"💬 Feedback: {feedback}")
        else:
            st.info("Silakan ekstrak metadata terlebih dahulu di tab 'Ekstraksi Metadata'")

    # Continue with other tabs...
    with tab3:
        st.header("📊 Analisis Batch Metadata")
        st.info("Tab ini akan dikembangkan untuk analisis batch multiple dokumen")

    with tab4:
        st.header("🔗 Linked Data Generation")
        if "current_metadata" in st.session_state:
            if st.button("Generate Linked Data"):
                # Implement linked data generation
                st.json({"@context": "Work in progress"})
        else:
            st.info("Silakan ekstrak metadata terlebih dahulu")

    with tab5:
        st.header("📊 Dashboard Metadata")
        
        stats = agent.db.get_statistics()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Records", stats["total_records"])
        with col2:
            st.metric("Avg Confidence", f"{stats['average_confidence']:.3f}")
        with col3:
            st.metric("Avg Completeness", f"{stats['average_completeness']:.3f}")
        
        # Schema distribution
        if stats["schema_distribution"]:
            st.subheader("📈 Distribusi Skema")
            df_schema = pd.DataFrame(list(stats["schema_distribution"].items()), 
                                   columns=["Schema", "Count"])
            st.bar_chart(df_schema.set_index("Schema"))

    with tab6:
        st.header("📋 Riwayat Metadata")
        
        history = agent.db.get_metadata_history(limit=20)
        
        if history:
            # Convert to DataFrame
            df = pd.DataFrame(history)
            
            # Display table
            st.dataframe(
                df[["file_name", "confidence_score", "completeness_score", 
                   "validation_status", "created_at"]],
                use_container_width=True
            )
            
            # Export options
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📥 Export CSV"):
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name="metadata_history.csv",
                        mime="text/csv"
                    )
            
            with col2:
                if st.button("📥 Export JSON"):
                    json_data = df.to_json(orient="records", indent=2)
                    st.download_button(
                        label="Download JSON",
                        data=json_data,
                        file_name="metadata_history.json",
                        mime="application/json"
                    )
        else:
            st.info("Belum ada riwayat metadata. Mulai dengan mengekstrak metadata pada tab pertama.")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <p>🤖 Enhanced Metadata Curator Agent - Powered by Google Gemini AI</p>
            <p>Human-in-the-Loop System untuk Data Governance Excellence</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
