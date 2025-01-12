# app.py
import streamlit as st
from anthropic import Anthropic
import time
from config import Config
from utils import (
    encode_image_to_base64, 
    validate_image, 
    save_analysis_history,
    load_analysis_history,
    get_analysis_by_image_name,
    delete_analysis_history,
    clear_analysis_history
)
from fpdf import FPDF, XPos, YPos
from PIL import Image
from io import BytesIO
import base64
from datetime import datetime
import tempfile
import os

# Initialize Anthropic client with API key check
def init_anthropic():
    if not Config.ANTHROPIC_API_KEY:
        st.error("❌ No API key found! Please check your .env file.")
        st.info("💡 Make sure your .env file contains: ANTHROPIC_API_KEY=your_key_here")
        return None
    try:
        return Anthropic(api_key=Config.ANTHROPIC_API_KEY)
    except Exception as e:
        st.error(f"❌ Error initializing Anthropic client: {str(e)}")
        return None

def create_pdf_report(analysis, uploaded_file, filename):
    """Create a PDF report with the analysis and image"""
    pdf = FPDF()
    pdf.add_page()
    
    # Add title
    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(0, 10, 'Analysis Report', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.ln(10)
    
    # Add timestamp
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 10, f'Report Generated: {time.strftime("%Y-%m-%d %H:%M:%S")}', 
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(10)
    
    # Add image if available
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            if isinstance(uploaded_file, BytesIO):
                image = Image.open(uploaded_file)
            else:
                uploaded_file.seek(0)
                image = Image.open(uploaded_file)
            
            image.save(tmp_file.name, 'JPEG')
            pdf.image(tmp_file.name, x=10, y=None, w=190)
            os.unlink(tmp_file.name)
            
        pdf.ln(10)
    except Exception as e:
        pdf.cell(0, 10, f'Error loading image: {str(e)}', 
                new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # Add analysis text
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 10, 'Analysis Results:', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(5)
    
    pdf.set_font('Helvetica', '', 11)
    try:
        paragraphs = analysis.split('\n')
        for paragraph in paragraphs:
            if paragraph.strip():
                cleaned_text = paragraph.strip().encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 10, cleaned_text)
                pdf.ln(5)
    except Exception as e:
        pdf.cell(0, 10, f'Error adding analysis text: {str(e)}', 
                new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    try:
        return bytes(pdf.output())
    except Exception as e:
        raise Exception(f"Error generating PDF: {str(e)}")

def get_claude_analysis(image_base64, anthropic_client):
    """Get TB analysis from Claude for the X-ray image"""
    if not anthropic_client:
        return False, "Anthropic client not initialized"
    
    try:
        st.info(f"📊 Using model: {Config.MODEL_NAME}")
        
        message = anthropic_client.messages.create(
            model=Config.MODEL_NAME,
            max_tokens=Config.MAX_TOKENS,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Please analyze this chest X-ray image for signs of tuberculosis. 
                        Provide your analysis in two parts:

                        PART 1 - Detailed Analysis:
                        1. Image Quality Assessment:
                           - Overall image quality
                           - Patient positioning
                           - Technical factors

                        2. Systematic Analysis:
                           - Lung fields
                           - Heart and mediastinum
                           - Pleural spaces
                           - Bones and soft tissues

                        3. TB-Specific Findings:
                           - Presence of infiltrates
                           - Cavity formations
                           - Lymph node involvement
                           - Distribution pattern

                        4. Severity Assessment:
                           - Extent of involvement
                           - Stage of disease
                           - Possible complications

                        5. Recommendations:
                           - Additional views if needed
                           - Further investigations
                           - Follow-up timeline

                        PART 2 - JSON Summary:
                        Provide a JSON summary with this structure:
                        {
                            "image_quality": {
                                "overall_quality": "",
                                "positioning": "",
                                "technical_factors": ""
                            },
                            "key_findings": {
                                "infiltrates": "present/absent",
                                "cavities": "present/absent",
                                "lymph_nodes": "involved/not involved",
                                "distribution": "",
                                "affected_areas": []
                            },
                            "severity": {
                                "stage": "",
                                "extent": "",
                                "complications": []
                            },
                            "tb_likelihood": "high/medium/low",
                            "recommendations": {
                                "additional_views": [],
                                "further_tests": [],
                                "follow_up": ""
                            }
                        }
                        
                        Separate the detailed analysis and JSON with ---"""
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_base64
                        }
                    }
                ]
            }]
        )

        analysis_text = message.content[0].text
        
        # Split the response into analysis and JSON parts
        parts = analysis_text.split('---')
        
        if len(parts) >= 2:
            detailed_analysis = parts[0].strip()
            json_summary = parts[1].strip()
            
            # Format the output with clear separation
            formatted_output = f"{detailed_analysis}\n\nJSON SUMMARY:\n```json\n{json_summary}\n```"
            return True, formatted_output
        else:
            return True, analysis_text
            
    except Exception as e:
        error_msg = f"Error analyzing image: {str(e)}"
        st.error(f"❌ {error_msg}")
        
        if hasattr(e, 'response'):
            st.error(f"📝 Response details: {e.response.text if hasattr(e.response, 'text') else 'No response text'}")
        return False, error_msg

def get_general_image_analysis(image_base64, anthropic_client):
    """Get general analysis for any type of image"""
    if not anthropic_client:
        return False, "Anthropic client not initialized"
    
    try:
        message = anthropic_client.messages.create(
            model=Config.MODEL_NAME,
            max_tokens=Config.MAX_TOKENS,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Please analyze this image and provide:
                        1. Description of what you see in the image
                        2. Main objects/subjects
                        3. Activities or actions (if any)
                        4. Setting or context
                        5. Notable details or features
                        6. Any text visible in the image
                        7. Quality and clarity of the image
                        
                        Also provide a JSON summary with:
                        {
                            "main_subject": "",
                            "objects_detected": [],
                            "setting": "",
                            "activities": [],
                            "text_detected": "",
                            "image_quality": "",
                            "colors": [],
                            "additional_notes": ""
                        }
                        
                        Separate the detailed analysis and JSON with ---"""
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_base64
                        }
                    }
                ]
            }]
        )

        analysis_text = message.content[0].text
        
        # Split the response into analysis and JSON parts
        parts = analysis_text.split('---')
        
        if len(parts) >= 2:
            detailed_analysis = parts[0].strip()
            json_summary = parts[1].strip()
            
            # Format the output with clear separation
            formatted_output = f"{detailed_analysis}\n\nJSON SUMMARY:\n```json\n{json_summary}\n```"
            return True, formatted_output
        else:
            return True, analysis_text
            
    except Exception as e:
        error_msg = f"Error analyzing image: {str(e)}"
        st.error(f"❌ {error_msg}")
        return False, error_msg

def display_history_card(entry, on_delete_callback=None):
    """Display a single history entry as a card"""
    with st.container():
        col1, col2 = st.columns([0.95, 0.05])
        
        with col1:
            with st.expander(f"📄 {entry['image_name']} - {entry['timestamp']}", expanded=False):
                if entry.get('image_data'):
                    try:
                        image_bytes = base64.b64decode(entry['image_data'])
                        image = Image.open(BytesIO(image_bytes))
                        st.image(image, caption='X-ray Image', use_container_width=True)
                    except Exception as e:
                        st.warning("Unable to load image from history")
                
                st.markdown("### Analysis Results")
                st.write(entry['analysis'])
                
                download_col1, download_col2 = st.columns(2)
                with download_col1:
                    try:
                        if entry.get('image_data'):
                            image_bytes = base64.b64decode(entry['image_data'])
                            pdf_bytes = create_pdf_report(
                                entry['analysis'], 
                                BytesIO(image_bytes), 
                                f"analysis_{entry['timestamp']}.pdf"
                            )
                            st.download_button(
                                label="📥 Download PDF",
                                data=pdf_bytes,
                                file_name=f"analysis_{entry['timestamp']}.pdf",
                                mime="application/pdf",
                                key=f"pdf_{entry['timestamp']}"
                            )
                    except Exception as e:
                        st.error(f"Error creating PDF: {str(e)}")
                
                with download_col2:
                    st.download_button(
                        label="📥 Download Text",
                        data=entry['analysis'],
                        file_name=f"analysis_{entry['timestamp']}.txt",
                        mime="text/plain",
                        key=f"text_{entry['timestamp']}"
                    )
        
        with col2:
            if st.button("🗑️", key=f"delete_{entry['timestamp']}"):
                success, message = delete_analysis_history(entry['image_name'])
                if success:
                    st.success("Analysis deleted successfully")
                    st.rerun()
                else:
                    st.error(f"Error deleting analysis: {message}")

def show_history_tab():
    """Display history tab with cards"""
    st.title("📜 Analysis History")
    
    history = load_analysis_history()
    
    if not history:
        st.info("No analysis history available yet")
        return
    
    history.sort(key=lambda x: x['timestamp'], reverse=True)
    
    st.sidebar.title("🔍 Filter History")
    date_filter = st.sidebar.date_input(
        "Filter by date",
        value=None,
        help="Show only analyses from this date"
    )
    
    search_term = st.sidebar.text_input(
        "Search in filenames",
        help="Filter by image filename"
    ).lower()
    
    if st.sidebar.button("🗑️ Clear All History", key="clear_all_button"):
        confirm = st.sidebar.checkbox("Confirm deletion of all history?", key="confirm_clear")
        if confirm:
            success, message = clear_analysis_history()
            if success:
                st.sidebar.success("All history cleared successfully")
                st.rerun()
            else:
                st.sidebar.error(f"Error clearing history: {message}")
    
    filtered_history = history
    if date_filter:
        filtered_history = [
            entry for entry in filtered_history 
            if datetime.strptime(entry['timestamp'], "%Y-%m-%d %H:%M:%S").date() == date_filter
        ]
    
    if search_term:
        filtered_history = [
            entry for entry in filtered_history 
            if search_term in entry['image_name'].lower()
        ]
    
    st.write(f"Showing {len(filtered_history)} of {len(history)} analyses")
    
    for entry in filtered_history:
        display_history_card(entry)

def create_sidebar():
    """Create sidebar with information and settings"""
    st.sidebar.title("ℹ️ About")
    st.sidebar.info(
        "This application uses Claude AI to analyze chest X-rays "
        "for signs of tuberculosis. Upload an X-ray image to get "
        "a detailed analysis and recommendations."
    )
    
    st.sidebar.title("⚙️ Settings")
    st.sidebar.write("📦 Maximum image size:", f"{Config.MAX_IMAGE_SIZE/1024/1024}MB")
    st.sidebar.write("🖼️ Supported formats:", ", ".join(Config.ALLOWED_EXTENSIONS))
    
    st.sidebar.title("🔌 API Status")
    if Config.ANTHROPIC_API_KEY:
        st.sidebar.success("API Key configured")
    else:
        st.sidebar.error("No API Key found")

def main():
    st.set_page_config(
        page_title="Image Analysis Assistant",
        page_icon="🔍",
        layout="wide"
    )
    
    tab1, tab2, tab3 = st.tabs(["🫁 TB Analysis", "📷 General Image Analysis", "📜 History"])
    
    anthropic_client = init_anthropic()
    
    with tab1:
        st.title("🫁 TB X-ray Analysis Assistant")
        create_sidebar()
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📤 Upload X-ray Image")
            uploaded_file = st.file_uploader(
                "Choose an X-ray image...", 
                type=list(Config.ALLOWED_EXTENSIONS),
                key="xray_uploader"
            )
            
            if uploaded_file is not None:
                is_valid, message = validate_image(uploaded_file, Config.MAX_IMAGE_SIZE)
                
                if not is_valid:
                    st.error(f"❌ {message}")
                    return
                
                st.image(uploaded_file, caption='Uploaded X-ray Image')  # Without 'use_container_width'
                
                if st.button('🔍 Analyze X-ray', type='primary', key="xray_analyze"):
                    if not anthropic_client:
                        st.error("❌ Cannot analyze: API client not initialized")
                        return
                        
                    with st.spinner('🔄 Analyzing image... This may take a few moments.'):
                        image_base64 = encode_image_to_base64(uploaded_file)
                        
                        if image_base64:
                            success, analysis = get_claude_analysis(image_base64, anthropic_client)
                            
                            with col2:
                                st.subheader("📋 Analysis Results")
                                if success:
                                    st.success("✅ Analysis completed successfully!")
                                    st.write(analysis)
                                    
                                    save_analysis_history(
                                        uploaded_file.name,
                                        image_base64,
                                        analysis
                                    )
                                    
                                    timestamp = time.strftime("%Y%m%d-%H%M%S")
                                    
                                    try:
                                        pdf_filename = f"analysis_{timestamp}.pdf"
                                        pdf_bytes = create_pdf_report(analysis, uploaded_file, pdf_filename)
                                        st.download_button(
                                            label="⬇️ Download PDF Report",
                                            data=pdf_bytes,
                                            file_name=pdf_filename,
                                            mime="application/pdf",
                                            key='pdf_download_tb'
                                        )
                                    except Exception as e:
                                        st.error(f"Error creating PDF: {str(e)}")
                                    
                                    st.download_button(
                                        label="⬇️ Download Text Report",
                                        data=analysis,
                                        file_name=f"analysis_{timestamp}.txt",
                                        mime="text/plain",
                                        key='text_download_tb'
                                    )
                                else:
                                    st.error(f"❌ {analysis}")
                        else:
                            st.error("❌ Error processing the image. Please try again.")
    
    with tab2:
        st.title("📷 General Image Analysis")
        st.info("Upload any image and I'll analyze its contents!")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📤 Upload Image")
            general_image = st.file_uploader(
                "Choose any image...", 
                type=list(Config.ALLOWED_EXTENSIONS),
                key="general_uploader"
            )
            
            if general_image is not None:
                is_valid, message = validate_image(general_image, Config.MAX_IMAGE_SIZE)
                
                if not is_valid:
                    st.error(f"❌ {message}")
                    return
                
                st.image(general_image, caption='Uploaded Image', use_container_width=True)
                
                if st.button('🔍 Analyze Image', type='primary', key="general_analyze"):
                    if not anthropic_client:
                        st.error("❌ Cannot analyze: API client not initialized")
                        return
                        
                    with st.spinner('🔄 Analyzing image... This may take a few moments.'):
                        image_base64 = encode_image_to_base64(general_image)
                        
                        if image_base64:
                            success, analysis = get_general_image_analysis(image_base64, anthropic_client)
                            
                            with col2:
                                st.subheader("📋 Analysis Results")
                                if success:
                                    st.success("✅ Analysis completed successfully!")
                                    st.write(analysis)
                                    
                                    timestamp = time.strftime("%Y%m%d-%H%M%S")
                                    
                                    try:
                                        pdf_filename = f"general_analysis_{timestamp}.pdf"
                                        pdf_bytes = create_pdf_report(analysis, general_image, pdf_filename)
                                        st.download_button(
                                            label="⬇️ Download PDF Report",
                                            data=pdf_bytes,
                                            file_name=pdf_filename,
                                            mime="application/pdf",
                                            key='pdf_download_general'
                                        )
                                    except Exception as e:
                                        st.error(f"Error creating PDF: {str(e)}")
                                    
                                    st.download_button(
                                        label="⬇️ Download Text Report",
                                        data=analysis,
                                        file_name=f"general_analysis_{timestamp}.txt",
                                        mime="text/plain",
                                        key='text_download_general'
                                    )
                                else:
                                    st.error(f"❌ {analysis}")
                        else:
                            st.error("❌ Error processing the image. Please try again.")
    
    with tab3:
        show_history_tab()

if __name__ == "__main__":
    main()
