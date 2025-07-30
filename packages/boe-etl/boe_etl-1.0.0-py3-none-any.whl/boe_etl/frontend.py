#!/usr/bin/env python3
"""
BoE ETL Frontend Module
=======================

Streamlit-based web frontend for the BoE ETL package.
Provides an easy-to-use interface for document processing.
"""

import streamlit as st
import pandas as pd
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import tempfile
import json
from datetime import datetime

# Add the package to the path for imports
sys.path.insert(0, str(Path(__file__).parent))

from .etl_pipeline import ETLPipeline
from .config import Config
from .schema_transformer import SchemaTransformer


def launch_frontend(port: int = 8501, host: str = "localhost", config_path: Optional[str] = None):
    """Launch the Streamlit frontend."""
    import subprocess
    
    # Get the path to this frontend module
    frontend_path = Path(__file__).resolve()
    
    # Build streamlit command
    cmd = [
        sys.executable, "-m", "streamlit", "run", 
        str(frontend_path),
        "--server.port", str(port),
        "--server.address", host
    ]
    
    if config_path:
        cmd.extend(["--", "--config", config_path])
    
    print(f"🚀 Launching BoE ETL Frontend...")
    print(f"📊 Opening at: http://{host}:{port}")
    print(f"⏹️  Press Ctrl+C to stop")
    print("-" * 50)
    
    # Launch streamlit
    subprocess.run(cmd)


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="BoE ETL Pipeline",
        page_icon="🏦",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🏦 BoE ETL Pipeline")
    st.markdown("**Financial Document Processing & NLP Analysis**")
    
    # Sidebar configuration
    st.sidebar.header("⚙️ Configuration")
    
    # Institution selection
    institutions = [
        "JPMorgan Chase", "Bank of America", "Citigroup", "Wells Fargo", "Goldman Sachs",
        "Morgan Stanley", "U.S. Bancorp", "PNC Financial", "Truist Financial", "Charles Schwab",
        "HSBC", "Barclays", "Lloyds Banking Group", "NatWest Group", "Standard Chartered",
        "Deutsche Bank", "BNP Paribas", "Credit Suisse", "UBS", "ING Group",
        "Santander", "BBVA", "UniCredit", "Intesa Sanpaolo", "Nordea",
        "Other"
    ]
    
    institution = st.sidebar.selectbox("🏛️ Institution", institutions)
    if institution == "Other":
        institution = st.sidebar.text_input("Enter Institution Name", "")
    
    # Quarter and Year selection
    quarters = ["Q1", "Q2", "Q3", "Q4"]
    years = [str(year) for year in range(2020, 2030)]
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        quarter = st.selectbox("📅 Quarter", quarters)
    with col2:
        year = st.selectbox("📅 Year", years, index=years.index("2025"))
    
    quarter_year = f"{quarter}_{year}"
    
    # User tracking
    uploaded_by = st.sidebar.text_input("👤 Uploaded By", "")
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["📄 Process Documents", "📊 View Results", "ℹ️ Help"])
    
    with tab1:
        st.header("📄 Document Processing")
        
        if not institution or not uploaded_by:
            st.warning("⚠️ Please fill in Institution and Uploaded By fields in the sidebar.")
            return
        
        # File upload
        uploaded_files = st.file_uploader(
            "Choose files to process",
            accept_multiple_files=True,
            type=['pdf', 'txt', 'xlsx', 'xls', 'csv', 'json']
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) uploaded")
            
            # Display file information
            for file in uploaded_files:
                st.write(f"📎 {file.name} ({file.size:,} bytes)")
            
            # Processing options
            st.subheader("🔧 Processing Options")
            
            col1, col2 = st.columns(2)
            with col1:
                output_format = st.selectbox("Output Format", ["CSV", "Parquet", "JSON"])
            with col2:
                include_nlp = st.checkbox("Include NLP Features", value=True)
            
            # Process button
            if st.button("🚀 Process Documents", type="primary"):
                process_documents(uploaded_files, institution, quarter_year, uploaded_by, output_format, include_nlp)
    
    with tab2:
        st.header("📊 Processing Results")
        display_results()
    
    with tab3:
        st.header("ℹ️ Help & Documentation")
        display_help()


def process_documents(files, institution: str, quarter_year: str, uploaded_by: str, output_format: str, include_nlp: bool):
    """Process uploaded documents."""
    try:
        # Initialize pipeline
        config = Config()
        pipeline = ETLPipeline(config=config)
        transformer = SchemaTransformer()
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        all_results = []
        
        for i, file in enumerate(files):
            status_text.text(f"Processing {file.name}...")
            progress_bar.progress((i + 1) / len(files))
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.name).suffix) as tmp_file:
                tmp_file.write(file.getvalue())
                tmp_path = Path(tmp_file.name)
            
            try:
                # Process file
                results = pipeline.process_file(tmp_path, institution, quarter_year)
                
                if include_nlp and results:
                    # Add NLP features
                    df = pd.DataFrame(results)
                    enhanced_results = transformer.add_nlp_features(df)
                    results = enhanced_results.to_dict('records')
                
                # Add metadata
                for result in results:
                    result['uploaded_by'] = uploaded_by
                    result['upload_timestamp'] = datetime.now().isoformat()
                    result['source_file'] = file.name
                
                all_results.extend(results)
                
            except Exception as e:
                st.error(f"Error processing {file.name}: {str(e)}")
            finally:
                # Clean up temp file
                if tmp_path.exists():
                    tmp_path.unlink()
        
        if all_results:
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{institution}_{quarter_year}_PureETL_{uploaded_by}_{timestamp}"
            
            if output_format == "CSV":
                df = pd.DataFrame(all_results)
                csv_data = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name=f"{filename}.csv",
                    mime="text/csv"
                )
            elif output_format == "Parquet":
                df = pd.DataFrame(all_results)
                parquet_data = df.to_parquet(index=False)
                st.download_button(
                    label="📥 Download Parquet",
                    data=parquet_data,
                    file_name=f"{filename}.parquet",
                    mime="application/octet-stream"
                )
            elif output_format == "JSON":
                json_data = json.dumps(all_results, indent=2, ensure_ascii=False)
                st.download_button(
                    label="📥 Download JSON",
                    data=json_data,
                    file_name=f"{filename}.json",
                    mime="application/json"
                )
            
            # Display summary
            st.success(f"✅ Processing complete! Generated {len(all_results)} records.")
            
            # Show preview
            if all_results:
                st.subheader("📋 Data Preview")
                df_preview = pd.DataFrame(all_results[:10])  # Show first 10 rows
                st.dataframe(df_preview)
                
                # Show statistics
                st.subheader("📈 Statistics")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Records", len(all_results))
                with col2:
                    st.metric("Files Processed", len(files))
                with col3:
                    st.metric("Institution", institution)
                with col4:
                    st.metric("Quarter", quarter_year)
        
        else:
            st.warning("⚠️ No data was extracted from the uploaded files.")
        
        progress_bar.progress(1.0)
        status_text.text("✅ Processing complete!")
        
    except Exception as e:
        st.error(f"❌ Processing failed: {str(e)}")


def display_results():
    """Display processing results and history."""
    st.write("📊 View your processed data and download results here.")
    
    # This would typically connect to a database or file system
    # For now, show placeholder content
    st.info("💡 Processed files will appear here after processing documents in the first tab.")


def display_help():
    """Display help and documentation."""
    st.markdown("""
    ## 🚀 Getting Started
    
    1. **Select Institution**: Choose your financial institution from the dropdown
    2. **Set Quarter/Year**: Select the reporting period
    3. **Enter Your Name**: For tracking and accountability
    4. **Upload Files**: Drag and drop or browse for documents
    5. **Process**: Click the process button to extract and analyze data
    
    ## 📁 Supported File Types
    
    - **PDF**: Earnings call transcripts, financial reports
    - **Excel/CSV**: Spreadsheet data, financial metrics
    - **Text**: Plain text transcripts and documents
    - **JSON**: Structured data files
    
    ## 📊 Output Features
    
    - **Structured Data**: Standardized schema for NLP analysis
    - **Speaker Identification**: Automatic role detection (CEO, CFO, etc.)
    - **Financial Terms**: Extraction of key financial vocabulary
    - **Topic Classification**: Automatic categorization of content
    - **Data Quality**: Missing value handling and validation
    
    ## 🏷️ Naming Convention
    
    Output files follow the format:
    `Institution_Quarter_Year_PureETL_User_Timestamp`
    
    Example: `JPMorgan_Q1_2025_PureETL_JohnSmith_20250526_143022`
    
    ## 🔧 Technical Details
    
    - Built with Streamlit and pandas
    - Uses PyMuPDF for PDF processing
    - Implements standardized financial NLP schema
    - Supports batch processing of multiple files
    - Includes comprehensive error handling
    
    ## 📞 Support
    
    For technical support or questions, please contact the ETL team.
    """)


if __name__ == "__main__":
    main()