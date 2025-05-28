# Metadata Curator Agent 🏛️

AI Agent untuk Manajemen Metadata Arsip dengan Human-in-the-Loop menggunakan Google Gemini AI dan Streamlit.

## 🎯 Fitur Utama

### 1. Ekstraksi Metadata Otomatis
- Mengekstrak metadata dari berbagai format dokumen (TXT, PDF, DOC, DOCX)
- Mendukung input manual untuk teks
- Menggunakan AI Gemini untuk analisis konten yang cerdas
- Confidence scoring untuk setiap hasil ekstraksi

### 2. Standar Metadata yang Didukung
- **Dublin Core**: 15 elemen standar metadata
- **ISAD(G)**: International Standard Archival Description (General)
- Skema metadata internal yang dapat dikustomisasi

### 3. Validasi Metadata Komprehensif
- Validasi format dan kelengkapan
- Deteksi field yang hilang atau tidak valid
- Skor kelengkapan metadata
- Human-in-the-loop validation dengan feedback system

### 4. Deteksi Inkonsistensi
- Analisis batch untuk multiple dokumen
- Deteksi variasi format tanggal
- Identifikasi inkonsistensi naming convention
- Pattern analysis untuk standarisasi

### 5. Linked Data Generation
- Konversi metadata ke format JSON-LD
- Mapping ke vocabulary standar (Dublin Core, Schema.org)
- Support untuk semantic web technologies
- Export dalam format yang interoperable

### 6. Reporting dan Analytics
- Laporan komprehensif dengan metrics
- Export ke CSV dan JSON
- Tracking progress dan statistics
- Rekomendasi aksi berdasarkan analisis AI

## 🚀 Quick Start

### Option 1: Poetry (Recommended)
```bash
# Windows
setup_poetry.bat

# Linux/macOS  
chmod +x setup_poetry.sh
./setup_poetry.sh

# Manual Poetry setup
poetry install
poetry run streamlit run metadata_curator_agent.py
```

### Option 2: Pip
```bash
# Windows
install.bat

# Linux/macOS
chmod +x install.sh
./install.sh

# Manual pip setup
pip install -r requirements.txt
streamlit run metadata_curator_agent.py
```

## 📦 Dependency Management

Project ini mendukung dua metode manajemen dependency:

1. **Poetry** (Recommended) - Modern dependency management
2. **pip + requirements.txt** - Traditional approach

### Poetry Benefits:
- Automatic virtual environment management
- Lock file untuk reproducible builds  
- Dependency groups (dev, test, docs)
- Built-in scripts dan task automation
- Better dependency resolution

Lihat [POETRY_GUIDE.md](POETRY_GUIDE.md) untuk panduan lengkap Poetry.

## 🛠️ Development Setup

### With Poetry:
```bash
# Setup development environment
poetry install --with dev,test,docs
poetry run pre-commit install

# Run tests
poetry run pytest

# Code formatting
poetry run black .
poetry run flake8

# Type checking  
poetry run mypy .
```

### With Make (Unix/Linux/macOS):
```bash
# Setup development environment
make dev-setup

# Run all quality checks
make check-all

# Run application
make run-enhanced
```

## 📖 Cara Penggunaan

### 1. Ekstraksi Metadata
1. Pilih tab "Ekstraksi Metadata"
2. Upload file atau input teks manual
3. Klik "Ekstrak Metadata" untuk analisis AI
4. Review hasil dan confidence score

### 2. Validasi Metadata
1. Pindah ke tab "Validasi Metadata"
2. Review hasil validasi otomatis
3. Lakukan validasi manual (Human-in-the-Loop)
4. Berikan feedback untuk improvement

### 3. Deteksi Inkonsistensi
1. Gunakan tab "Deteksi Inkonsistensi"
2. Analisis batch metadata untuk pattern
3. Review inkonsistensi yang terdeteksi
4. Implementasi standardisasi

### 4. Generate Linked Data
1. Buka tab "Linked Data"
2. Generate JSON-LD dari metadata
3. Download untuk integrasi dengan sistem lain

### 5. Generate Laporan
1. Akses tab "Laporan"
2. Generate laporan komprehensif
3. Export dalam format CSV atau JSON
4. Review rekomendasi aksi

## 🏗️ Arsitektur Sistem

### Core Components
- **MetadataCuratorAgent**: Main class untuk semua operasi metadata
- **Gemini Integration**: AI-powered content analysis
- **Validation Engine**: Multi-schema validation system
- **Linked Data Generator**: Semantic web data conversion
- **Reporting System**: Analytics dan metrics

### Human-in-the-Loop (HITL)
- Manual validation interface
- Feedback collection system
- Continuous learning mechanism
- Quality assurance workflow

### Supported Schemas
- Dublin Core (15 elements)
- ISAD(G) (17 descriptive elements)
- Extensible untuk schema custom

## 📊 Kontribusi pada IKU Data Governance

### Indeks Ketersediaan Arsip
- Metadata berkualitas tinggi meningkatkan discoverability
- Standardisasi format untuk konsistensi
- Automatic tagging dan categorization

### Indeks Pelayanan Informasi Kearsipan
- Enhanced search capabilities
- Better content understanding
- Improved user experience dalam information retrieval

## 🔧 Konfigurasi Lanjutan

### Custom Schema
Tambahkan schema metadata custom di class `MetadataCuratorAgent`:

```python
self.custom_schema = {
    "field1": "Description 1",
    "field2": "Description 2",
    # ... tambah field lainnya
}
```

### API Integration
Untuk integrasi dengan sistem eksternal:

```python
# Contoh endpoint untuk batch processing
@app.route('/api/extract', methods=['POST'])
def extract_metadata_api():
    # Implementation here
    pass
```

## 🛠️ Troubleshooting

### Common Issues
1. **API Key Error**: Pastikan Gemini API Key valid dan aktif
2. **File Upload Error**: Check format file yang didukung
3. **Validation Errors**: Review schema requirements

### Performance Tips
- Batasi ukuran file untuk processing optimal
- Gunakan batch processing untuk multiple files
- Monitor confidence scores untuk quality control

## 📝 Roadmap

### v1.1
- [ ] Support PDF text extraction
- [ ] Batch file processing
- [ ] Advanced analytics dashboard

### v1.2
- [ ] Machine learning model training
- [ ] Custom schema builder
- [ ] Integration dengan repository systems

### v1.3
- [ ] Multi-language support
- [ ] Advanced NLP features
- [ ] Automated workflow triggers

## 🤝 Contributing

Kontribusi sangat diterima! Silakan:
1. Fork repository
2. Create feature branch
3. Commit changes
4. Push ke branch
5. Create Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

Untuk pertanyaan atau dukungan:
- Create issue di repository
- Contact: [your-email@domain.com]
- Documentation: [link-to-docs]

---

**Metadata Curator Agent** - Empowering Data Governance through AI-Human Collaboration 🤖🤝👨‍💼
