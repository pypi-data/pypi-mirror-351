# 🔧 Pure Financial Document ETL Pipeline

A **data engineering focused** ETL pipeline that extracts from unstructured financial document data (pdf, spreadsheet, doc) without making analytical assumptions or classifications.

## 🎯 **Pure ETL Philosophy**

This pipeline follows **separation of concerns** principles:

- **ETL Layer**: Extract → Structure → Export (no analysis)
- **Analysis Layer**: Separate downstream processing for ML/NLP

## 📦 Installation

### From PyPI
```bash
pip install boe-etl
```

### From Source
```bash
git clone https://github.com/daleparr/boe-etl.git
cd boe-etl
pip install -e .
```

### With Optional Dependencies
```bash
# For web frontend
pip install boe-etl[frontend]

# For development
pip install boe-etl[dev]

# All dependencies
pip install boe-etl[all]
```

## 🚀 **Quick Start**

### **Installation**
```bash
pip install boe-etl
```

### **Launch Web Interface**
```bash
boe-etl frontend
```

### **Access Application**
Open your browser to: `http://localhost:8501`

## 📊 **What This ETL Does**

### **✅ Raw Data Extraction**
- **PDF Documents**: Text extraction from earnings reports
- **Excel Files**: Multi-sheet data extraction
- **Text Files**: Direct text processing
- **Sentence Segmentation**: Clean, structured sentences

### **✅ Raw Feature Extraction**
- **`all_financial_terms`**: Financial vocabulary found (no classification)
- **`financial_figures`**: Numbers and amounts extracted (no interpretation)
- **`temporal_indicators`**: Time-related language (no actual/projection labels)
- **`speaker_raw`**: Speaker patterns identified (no role classification)

### **✅ Factual Boolean Flags**
- **`has_financial_terms`**: Terms present or not
- **`has_financial_figures`**: Figures present or not
- **`has_temporal_language`**: Temporal words present or not
- **`has_speaker_identified`**: Speaker pattern found or not

## 🚫 **What This ETL Does NOT Do**

### **❌ No Analytical Assumptions**
- No topic classification (Revenue & Growth, Risk Management, etc.)
- No actual vs projection classification
- No financial content relevance scoring
- No speaker role interpretation (CEO, CFO, Analyst)

### **❌ No Machine Learning**
- No topic modeling
- No sentiment analysis
- No content classification
- No predictive features

## 📈 **Output Schema**

### **Core Fields**
```csv
source_file,institution,quarter,sentence_id,speaker_raw,text,source_type
```

### **Raw Extraction Fields**
```csv
all_financial_terms,financial_figures,financial_figures_text,temporal_indicators
```

### **Factual Flags**
```csv
has_financial_terms,has_financial_figures,has_temporal_language,has_speaker_identified
```

### **Metadata**
```csv
word_count,char_count,processing_date,extraction_timestamp
```

## 🔄 **Example Processing**

### **Input Document**
```
"We reported revenue of $2.5 billion this quarter, up 15% from last year."
```

### **Pure ETL Output**
```csv
all_financial_terms: "revenue"
financial_figures: "$2.5 billion|15%"
temporal_indicators: "reported|this quarter|last year"
has_financial_terms: True
has_financial_figures: True
has_temporal_language: True
```

### **No Analysis Applied**
- ❌ No classification as "actual" vs "projection"
- ❌ No topic assignment like "Revenue & Growth"
- ❌ No sentiment or relevance scoring

## 🏗️ **Architecture**

### **Pure ETL Pipeline**
```
Documents → Extract Text → Segment Sentences → Extract Raw Features → Export CSV
```

### **Downstream Analysis (Separate)**
```
Raw CSV → Topic Modeling → Classification → Feature Engineering → ML Models
```

## 🛠️ **Technical Features**

### **✅ Missing Value Handling**
- No null values in output
- Consistent defaults for all fields
- NLP-ready datasets

### **✅ Multi-Format Support**
- PDF processing with PyPDF2
- Excel processing with openpyxl
- Text file processing
- Graceful error handling

### **✅ Web Interface**
- Drag-and-drop file upload
- Multi-institution processing
- Progress tracking
- Processing history
- CSV download

## 📚 **Use Cases**

### **Financial Institutions**
- Earnings call transcript processing
- Financial report data extraction
- Regulatory document structuring
- Multi-quarter analysis preparation

### **Research & Analytics**
- Academic financial research
- Market analysis preparation
- NLP model training data
- Time series analysis datasets

### **Compliance & Audit**
- Document processing audit trails
- Structured data for compliance
- Historical document analysis
- Regulatory reporting preparation

## 🔧 **Development**

### **Project Structure**
```
boe-etl/
├── boe_etl/
│   ├── core.py                # Main ETL pipeline
│   ├── parsers/              # Document parsers
│   ├── schema.py             # Data standardization
│   └── frontend.py           # Web interface
├── setup.py                  # Package configuration
├── requirements.txt          # Dependencies
└── README.md                 # This file
```

### **Dependencies**
- **streamlit**: Web interface framework
- **pandas**: Data manipulation
- **PyPDF2**: PDF text extraction
- **openpyxl**: Excel file processing

## 🏷️ **Naming Convention**

Output files follow the standardized format:
```
{Institution}_{Quarter}_{Year}_PureETL_{User}_{Timestamp}
```

Example: `JPMorgan_Q1_2025_PureETL_JohnSmith_20250526_143022.csv`

## 📄 **License**

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 **Contributing**

This is a pure ETL pipeline focused on data engineering principles. Contributions should maintain the separation between extraction and analysis.

### **Guidelines**
- Keep ETL layer free of analytical assumptions
- Maintain raw data extraction focus
- Preserve downstream analysis flexibility
- Follow data engineering best practices

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/daleparr/boe-etl/issues)
- **Documentation**: [GitHub Wiki](https://github.com/daleparr/boe-etl/wiki)
- **Email**: etl-team@bankofengland.co.uk

## 🎯 **Philosophy: Extract, Don't Analyze**

This pipeline embodies the principle that **ETL should extract and structure data, not make analytical decisions**. Analysis belongs in separate, specialized pipelines that can evolve independently.

**Pure ETL = Maximum Flexibility for Downstream Analysis** 🔧

---

**Version**: 1.0.0  
**Author**: Bank of England ETL Team  
**Repository**: https://github.com/daleparr/boe-etl
