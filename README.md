# README.md

# TB X-ray Analysis Application


This application uses Claude AI to analyze chest X-rays for signs of tuberculosis.

## Setup Instructions

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file and add your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```
5. Run the application:
   ```bash
   streamlit run app.py
   ```

## Features

- Upload and validate X-ray images
- AI-powered analysis using Claude
- Detailed report generation
- Analysis history tracking
- Download analysis reports
- User-friendly interface

## Requirements

- Python 3.8+
- Streamlit
- Anthropic API access
- PIL/Pillow
- python-dotenv

## Usage

1. Upload a chest X-ray image (JPG, JPEG, or PNG format)
2. Click "Analyze X-ray"
3. View the detailed analysis
4. Download the analysis report if needed

## Notes

- Maximum image size: 10MB
- Supported formats: PNG, JPG, JPEG
- Requires valid Anthropic API key
- Analysis history is stored locally
#   s m a r t - i m a g e - a n a l y s i s - a p p  
 