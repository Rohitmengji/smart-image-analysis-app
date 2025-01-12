# Vision Analysis Assistant 🔍

A powerful AI-powered application that combines medical X-ray analysis and general image analysis capabilities using Claude AI. The application provides detailed analysis, maintains history, and generates comprehensive reports.

## ✨ Features

### Medical X-ray Analysis
- Detailed TB screening analysis
- Structured medical findings
- Professional PDF report generation
- Medical terminology and observations

### General Image Analysis
- Comprehensive image content analysis
- Object and scene detection
- Text detection in images
- Color and quality assessment

### Additional Features
- Analysis history tracking
- Search and filter capabilities
- PDF and text report downloads
- Simple and intuitive interface

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Anthropic API key
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/vision-analysis-assistant.git
cd vision-analysis-assistant
```

2. Create a virtual environment:
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:
```env
ANTHROPIC_API_KEY=your_api_key_here
```

5. Run the application:
```bash
streamlit run app/app.py
```

## 📱 Usage

### TB X-ray Analysis
1. Select the "TB Analysis" tab
2. Upload a chest X-ray image
3. Click "Analyze X-ray"
4. View detailed analysis and download reports

### General Image Analysis
1. Select the "General Image Analysis" tab
2. Upload any image
3. Click "Analyze Image"
4. View comprehensive analysis with JSON summary

### History Management
- View all previous analyses in the History tab
- Filter by date or filename
- Download previous reports
- Delete unwanted analyses

## 🛠️ Technologies Used
- Streamlit
- Anthropic Claude AI
- Python
- FPDF2
- PIL (Python Imaging Library)

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## 👥 Authors
- Rohit Mengji - *Initial work* - [Your GitHub Profile](https://github.com/Rohitmengji)

## 🙏 Acknowledgments
- Anthropic for Claude AI
- Streamlit team for the amazing framework
- Medical imaging community for inspiration

## 📞 Support
For support, email rohitmengjih@gmail.com or open an issue in the repository.

## 🔒 Security
Please do not commit any sensitive information like API keys. Use environment variables for sensitive data.
