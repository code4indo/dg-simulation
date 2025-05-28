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

# Konfigurasi halaman Streamlit
st.set_page_config(
    page_title="Metadata Curator Agent",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

class MetadataCuratorAgent:
    def __init__(self, api_key: str):
        """Initialize Metadata Curator Agent dengan Gemini AI"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
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
        Analisis konten berikut dan ekstrak metadata yang relevan sesuai dengan standar Dublin Core dan ISAD(G).
        
        Nama file: {file_name}
        Konten:
        {content[:3000]}  # Batasi untuk menghindari token limit
        
        Berikan output dalam format JSON dengan struktur berikut:
        {{
            "dublin_core": {{
                "title": "",
                "creator": "",
                "subject": "",
                "description": "",
                "publisher": "",
                "date": "",
                "type": "",
                "format": "",
                "language": "",
                "rights": ""
            }},
            "isad_g": {{
                "reference_code": "",
                "title": "",
                "date": "",
                "level_of_description": "",
                "name_of_creator": "",
                "scope_and_content": "",
                "language_of_material": ""
            }},
            "confidence_score": 0.0,
            "suggestions": []
        }}
        
        Berikan confidence score 0-1 untuk setiap field yang diekstrak.
        Sertakan saran untuk metadata yang mungkin hilang atau perlu diperbaiki.
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Parse JSON response
            metadata = json.loads(response.text)
            return metadata
        except Exception as e:
            st.error(f"Error dalam ekstraksi metadata: {str(e)}")
            return self._get_empty_metadata()

    def validate_metadata(self, metadata: Dict[str, Any], schema_type: str = "dublin_core") -> Dict[str, Any]:
        """Validasi metadata terhadap skema yang dipilih"""
        schema = self.dublin_core_schema if schema_type == "dublin_core" else self.isad_g_schema
        validation_results = {
            "is_valid": True,
            "missing_fields": [],
            "invalid_fields": [],
            "warnings": [],
            "completeness_score": 0.0
        }
        
        metadata_section = metadata.get(schema_type, {})
        
        # Cek field yang hilang
        for field in schema.keys():
            if field not in metadata_section or not metadata_section[field]:
                validation_results["missing_fields"].append(field)
        
        # Cek validitas format tanggal
        date_fields = ["date"] if schema_type == "dublin_core" else ["date"]
        for field in date_fields:
            if field in metadata_section and metadata_section[field]:
                if not self._is_valid_date(metadata_section[field]):
                    validation_results["invalid_fields"].append(f"{field}: format tanggal tidak valid")
        
        # Hitung skor kelengkapan
        filled_fields = sum(1 for field in schema.keys() if metadata_section.get(field))
        validation_results["completeness_score"] = filled_fields / len(schema)
        
        # Set status valid
        validation_results["is_valid"] = len(validation_results["missing_fields"]) == 0 and len(validation_results["invalid_fields"]) == 0
        
        return validation_results

    def suggest_metadata_improvements(self, metadata: Dict[str, Any], similar_records: List[Dict] = None) -> List[str]:
        """Berikan saran perbaikan metadata berdasarkan konteks dan arsip sejenis"""
        suggestions = []
        
        # Analisis menggunakan Gemini
        prompt = f"""
        Analisis metadata berikut dan berikan saran perbaikan berdasarkan best practices untuk metadata arsip:
        
        Metadata saat ini:
        {json.dumps(metadata, indent=2)}
        
        Berikan saran dalam format list untuk:
        1. Field yang hilang atau tidak lengkap
        2. Perbaikan format atau standarisasi
        3. Penambahan metadata yang dapat meningkatkan findability
        4. Konsistensi dengan standar Dublin Core/ISAD(G)
        
        Format output: list of strings
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Parse suggestions from response
            suggestions_text = response.text
            suggestions = [s.strip() for s in suggestions_text.split('\n') if s.strip() and not s.strip().startswith('#')]
        except Exception as e:
            suggestions.append(f"Error dalam analisis: {str(e)}")
        
        return suggestions

    def detect_inconsistencies(self, metadata_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Deteksi inkonsistensi dalam kumpulan metadata"""
        inconsistencies = {
            "format_inconsistencies": [],
            "naming_inconsistencies": [],
            "date_format_issues": [],
            "missing_patterns": []
        }
        
        # Analisis format tanggal
        date_formats = set()
        for metadata in metadata_list:
            date_val = metadata.get("dublin_core", {}).get("date", "")
            if date_val:
                date_formats.add(self._detect_date_format(date_val))
        
        if len(date_formats) > 1:
            inconsistencies["date_format_issues"].append(f"Ditemukan {len(date_formats)} format tanggal berbeda")
        
        # Analisis creator naming
        creators = []
        for metadata in metadata_list:
            creator = metadata.get("dublin_core", {}).get("creator", "")
            if creator:
                creators.append(creator)
        
        # Deteksi variasi nama yang mungkin sama
        unique_creators = set(creators)
        if len(unique_creators) != len(creators):
            inconsistencies["naming_inconsistencies"].append("Ditemukan variasi nama creator yang mungkin merujuk entitas sama")
        
        return inconsistencies

    def create_linked_data(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Buat linked data dari metadata"""
        linked_data = {
            "@context": {
                "dc": "http://purl.org/dc/elements/1.1/",
                "dcterms": "http://purl.org/dc/terms/",
                "foaf": "http://xmlns.com/foaf/0.1/",
                "schema": "http://schema.org/"
            },
            "@type": "schema:ArchivalResource"
        }
        
        # Map Dublin Core ke linked data
        dc_metadata = metadata.get("dublin_core", {})
        mapping = {
            "title": "dc:title",
            "creator": "dc:creator",
            "subject": "dc:subject",
            "description": "dc:description",
            "date": "dc:date",
            "type": "dc:type",
            "format": "dc:format",
            "language": "dc:language"
        }
        
        for field, property_name in mapping.items():
            if dc_metadata.get(field):
                linked_data[property_name] = dc_metadata[field]
        
        return linked_data

    def _get_empty_metadata(self) -> Dict[str, Any]:
        """Return empty metadata structure"""
        return {
            "dublin_core": {field: "" for field in self.dublin_core_schema.keys()},
            "isad_g": {field: "" for field in self.isad_g_schema.keys()},
            "confidence_score": 0.0,
            "suggestions": []
        }

    def _is_valid_date(self, date_string: str) -> bool:
        """Validasi format tanggal"""
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # DD/MM/YYYY
            r'\d{4}',              # YYYY
            r'\d{2}-\d{2}-\d{4}'   # DD-MM-YYYY
        ]
        return any(re.match(pattern, date_string.strip()) for pattern in date_patterns)

    def _detect_date_format(self, date_string: str) -> str:
        """Deteksi format tanggal"""
        if re.match(r'\d{4}-\d{2}-\d{2}', date_string):
            return "ISO (YYYY-MM-DD)"
        elif re.match(r'\d{2}/\d{2}/\d{4}', date_string):
            return "DD/MM/YYYY"
        elif re.match(r'\d{4}', date_string):
            return "Year only"
        else:
            return "Unknown format"

def main():
    st.title("🏛️ Metadata Curator Agent")
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
        st.markdown("### 📊 Statistik Sesi")
        if "processed_files" not in st.session_state:
            st.session_state.processed_files = 0
        if "validation_score" not in st.session_state:
            st.session_state.validation_score = 0.0
        
        st.metric("File Diproses", st.session_state.processed_files)
        st.metric("Skor Validasi Rata-rata", f"{st.session_state.validation_score:.2f}")

    # Initialize agent
    try:
        agent = MetadataCuratorAgent(api_key)
    except Exception as e:
        st.error(f"Error menginisialisasi agent: {str(e)}")
        st.stop()

    # Main interface tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📄 Ekstraksi Metadata", 
        "✅ Validasi Metadata", 
        "🔍 Deteksi Inkonsistensi", 
        "🔗 Linked Data", 
        "📊 Laporan"
    ])

    with tab1:
        st.header("Ekstraksi Metadata Otomatis")
        
        # Input method selection
        input_method = st.radio(
            "Pilih metode input:",
            ["Upload File", "Input Teks Manual"]
        )
        
        if input_method == "Upload File":
            uploaded_file = st.file_uploader(
                "Upload dokumen arsip",
                type=['txt', 'pdf', 'doc', 'docx', 'json'],
                help="Format yang didukung: TXT, PDF, DOC, DOCX, JSON"
            )
            
            if uploaded_file is not None:
                # Read file content
                if uploaded_file.type == "text/plain":
                    content = str(uploaded_file.read(), "utf-8")
                else:
                    content = f"File: {uploaded_file.name}\nType: {uploaded_file.type}\nSize: {uploaded_file.size} bytes"
                
                st.text_area("Preview Konten", content[:500] + "..." if len(content) > 500 else content, height=100)
                
                if st.button("🤖 Ekstrak Metadata", type="primary"):
                    with st.spinner("Menganalisis dokumen..."):
                        metadata = agent.extract_metadata_from_text(content, uploaded_file.name)
                        st.session_state.current_metadata = metadata
                        st.session_state.processed_files += 1
                    
                    # Display results
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Dublin Core")
                        dc_metadata = metadata.get("dublin_core", {})
                        for field, value in dc_metadata.items():
                            st.text_input(f"{field.replace('_', ' ').title()}", value, key=f"dc_{field}")
                    
                    with col2:
                        st.subheader("ISAD(G)")
                        isad_metadata = metadata.get("isad_g", {})
                        for field, value in list(isad_metadata.items())[:7]:  # Show first 7 fields
                            st.text_input(f"{field.replace('_', ' ').title()}", value, key=f"isad_{field}")
                    
                    # Confidence score and suggestions
                    st.subheader("📈 Analisis AI")
                    col1, col2 = st.columns(2)
                    with col1:
                        confidence = metadata.get("confidence_score", 0.0)
                        st.metric("Confidence Score", f"{confidence:.2f}")
                    with col2:
                        st.metric("Status", "✅ Berhasil" if confidence > 0.7 else "⚠️ Perlu Review")
                    
                    suggestions = metadata.get("suggestions", [])
                    if suggestions:
                        st.subheader("💡 Saran Perbaikan")
                        for i, suggestion in enumerate(suggestions[:5]):
                            st.info(f"{i+1}. {suggestion}")

        else:  # Manual text input
            manual_text = st.text_area(
                "Masukkan teks dokumen:",
                height=200,
                placeholder="Paste konten dokumen arsip di sini..."
            )
            
            file_name = st.text_input("Nama file (opsional):")
            
            if manual_text and st.button("🤖 Ekstrak Metadata", type="primary"):
                with st.spinner("Menganalisis teks..."):
                    metadata = agent.extract_metadata_from_text(manual_text, file_name)
                    st.session_state.current_metadata = metadata
                    st.session_state.processed_files += 1
                
                # Display results (same as above)
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Dublin Core")
                    dc_metadata = metadata.get("dublin_core", {})
                    for field, value in dc_metadata.items():
                        st.text_input(f"{field.replace('_', ' ').title()}", value, key=f"dc_manual_{field}")
                
                with col2:
                    st.subheader("ISAD(G)")
                    isad_metadata = metadata.get("isad_g", {})
                    for field, value in list(isad_metadata.items())[:7]:
                        st.text_input(f"{field.replace('_', ' ').title()}", value, key=f"isad_manual_{field}")

    with tab2:
        st.header("Validasi Metadata")
        
        if "current_metadata" in st.session_state:
            metadata = st.session_state.current_metadata
            
            # Validation
            validation_results = agent.validate_metadata(metadata, schema_type)
            
            # Display validation status
            col1, col2, col3 = st.columns(3)
            with col1:
                status = "✅ Valid" if validation_results["is_valid"] else "❌ Invalid"
                st.metric("Status Validasi", status)
            with col2:
                st.metric("Skor Kelengkapan", f"{validation_results['completeness_score']:.2f}")
            with col3:
                missing_count = len(validation_results["missing_fields"])
                st.metric("Field Hilang", missing_count)
            
            # Update session state
            st.session_state.validation_score = validation_results["completeness_score"]
            
            # Detailed validation results
            if validation_results["missing_fields"]:
                st.subheader("⚠️ Field yang Hilang")
                for field in validation_results["missing_fields"]:
                    st.warning(f"Field '{field}' tidak ada atau kosong")
            
            if validation_results["invalid_fields"]:
                st.subheader("❌ Field yang Tidak Valid")
                for field in validation_results["invalid_fields"]:
                    st.error(field)
            
            # Human-in-the-loop: Manual validation
            st.subheader("👤 Validasi Manual (Human-in-the-Loop)")
            human_validation = st.radio(
                "Apakah Anda menyetujui hasil ekstraksi metadata ini?",
                ["Belum ditentukan", "Setuju", "Perlu perbaikan", "Tolak"]
            )
            
            if human_validation != "Belum ditentukan":
                feedback = st.text_area(
                    "Feedback atau komentar:",
                    placeholder="Berikan feedback untuk meningkatkan akurasi AI..."
                )
                
                if st.button("💾 Simpan Validasi"):
                    st.success(f"Validasi disimpan: {human_validation}")
                    if feedback:
                        st.info(f"Feedback: {feedback}")
        else:
            st.info("Silakan ekstrak metadata terlebih dahulu di tab 'Ekstraksi Metadata'")

    with tab3:
        st.header("Deteksi Inkonsistensi")
        
        # Sample data untuk demo
        st.subheader("📊 Analisis Batch Metadata")
        
        if st.button("🔍 Analisis Inkonsistensi (Demo)"):
            # Create sample metadata for demonstration
            sample_metadata = [
                {
                    "dublin_core": {
                        "title": "Laporan Tahunan 2023",
                        "creator": "Departemen Keuangan",
                        "date": "2023-12-31",
                        "type": "Laporan"
                    }
                },
                {
                    "dublin_core": {
                        "title": "Annual Report 2023",
                        "creator": "Dept. Keuangan",
                        "date": "31/12/2023",
                        "type": "Report"
                    }
                },
                {
                    "dublin_core": {
                        "title": "Laporan Bulanan Januari",
                        "creator": "Departemen Keuangan",
                        "date": "2024-01",
                        "type": "Laporan"
                    }
                }
            ]
            
            inconsistencies = agent.detect_inconsistencies(sample_metadata)
            
            st.subheader("🚨 Inkonsistensi Terdeteksi")
            
            for category, issues in inconsistencies.items():
                if issues:
                    st.warning(f"**{category.replace('_', ' ').title()}:**")
                    for issue in issues:
                        st.write(f"• {issue}")
            
            if not any(inconsistencies.values()):
                st.success("✅ Tidak ada inkonsistensi terdeteksi!")

    with tab4:
        st.header("Linked Data Generation")
        
        if "current_metadata" in st.session_state:
            metadata = st.session_state.current_metadata
            
            if st.button("🔗 Generate Linked Data"):
                linked_data = agent.create_linked_data(metadata)
                
                st.subheader("📋 Linked Data (JSON-LD)")
                st.json(linked_data)
                
                # Download option
                json_string = json.dumps(linked_data, indent=2)
                st.download_button(
                    label="📥 Download JSON-LD",
                    data=json_string,
                    file_name="linked_data.jsonld",
                    mime="application/json"
                )
        else:
            st.info("Silakan ekstrak metadata terlebih dahulu")

    with tab5:
        st.header("Laporan Metadata")
        
        # Generate comprehensive report
        if st.button("📊 Generate Laporan"):
            if "current_metadata" in st.session_state:
                metadata = st.session_state.current_metadata
                validation_results = agent.validate_metadata(metadata, schema_type)
                suggestions = agent.suggest_metadata_improvements(metadata)
                
                # Report summary
                st.subheader("📋 Ringkasan Laporan")
                
                report_data = {
                    "Tanggal Laporan": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Skema yang Digunakan": "Dublin Core" if schema_type == "dublin_core" else "ISAD(G)",
                    "Skor Kelengkapan": f"{validation_results['completeness_score']:.2f}",
                    "Status Validasi": "Valid" if validation_results["is_valid"] else "Invalid",
                    "Jumlah Field Hilang": len(validation_results["missing_fields"]),
                    "Jumlah Saran": len(suggestions)
                }
                
                for key, value in report_data.items():
                    st.write(f"**{key}:** {value}")
                
                # Detailed sections
                st.subheader("🎯 Rekomendasi Aksi")
                for i, suggestion in enumerate(suggestions[:10], 1):
                    st.write(f"{i}. {suggestion}")
                
                # Export options
                st.subheader("📤 Export Laporan")
                col1, col2 = st.columns(2)
                
                with col1:
                    # CSV export
                    df = pd.DataFrame([report_data])
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📊 Download CSV",
                        data=csv,
                        file_name="metadata_report.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    # JSON export
                    full_report = {
                        "summary": report_data,
                        "metadata": metadata,
                        "validation": validation_results,
                        "suggestions": suggestions
                    }
                    json_report = json.dumps(full_report, indent=2)
                    st.download_button(
                        label="📄 Download JSON",
                        data=json_report,
                        file_name="metadata_report.json",
                        mime="application/json"
                    )
            else:
                st.warning("Tidak ada data metadata untuk dilaporkan. Silakan ekstrak metadata terlebih dahulu.")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <p>🤖 Metadata Curator Agent - Powered by Google Gemini AI</p>
            <p>Human-in-the-Loop System untuk Data Governance</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
