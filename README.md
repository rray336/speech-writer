# Speech Writer

AI-powered speech template and speech generator with dual interface options: a desktop Tkinter GUI and a modern Flask web application. Extracts speaker-specific prepared remarks from PDF transcripts and generates personalized templates and speeches.

## Features

### Core Functionality
- **LLM-Powered PDF Analysis**: AI extracts and identifies speaker-specific prepared remarks from transcripts
- **Direct Template Generation**: Creates structured speech templates directly from prepared remarks
- **Custom Speech Generation**: Converts key messages into full speeches using prepared remarks as style context
- **Multi-Provider AI Support**: OpenAI, Claude, Gemini, and OpenRouter integration

### User Interface Options
- **Flask Web Application**: Modern web-based interface with responsive design and real-time status updates
  - Clean 5-step workflow with progress tracking
  - AI model selection interface
  - Real-time processing status with progress bars
  - Export functionality for all generated content
  - Mobile-responsive design for any device
- **Desktop GUI (Legacy)**: Professional Tkinter interface with popup-based results
  - Streamlined 4-step workflow
  - Dedicated windows for templates and speeches with tabbed interface
  - Comprehensive logging with LLM prompt visibility

## Quick Start

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd speech-writer
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys (at least one required)
   ```

4. **Run the application**
   
   **Web Application (Recommended):**
   ```bash
   python web_app.py
   ```
   Then open your browser to `http://localhost:5000`
   
   **Desktop Application:**
   ```bash
   python main.py
   ```

### System Requirements
- Python 3.8 or higher
- Web browser (for web application) or GUI support (for desktop application)
- At least one AI provider API key

## Environment Variables

Create a `.env` file with your AI provider API keys:

```env
# At least one API key is required
OPENAI_API_KEY=your_openai_api_key_here
CLAUDE_API_KEY=your_claude_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Optional: Custom API endpoints
OPENAI_BASE_URL=https://api.openai.com/v1
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

## Usage Workflow

### Web Application Interface

#### Step 1: Upload PDF Transcript
- Click "Choose File" to select a PDF file containing speaker transcripts
- Supports transcripts with multiple speakers, Q&A sessions, prepared remarks
- Application validates file format and readability with real-time feedback

#### Step 2: Select AI Model
- Choose your preferred AI provider from the dropdown menu
- Available providers based on configured API keys
- Switch providers anytime without restarting the application

#### Step 3: Enter Speaker Name
- Enter the exact name of the speaker you want to extract content for
- Name matching is case-insensitive and flexible (supports variations)

#### Step 4: Generate Template
- Click "Generate Template" to extract prepared remarks and create speech template
- Real-time progress tracking with status updates
- Results display with prepared remarks and generated template
- Export options for template and prepared remarks

#### Step 5: Generate Custom Speech
- Enter your key messages in the text area
- Click "Generate Custom Speech" for full speech conversion
- Complete speech that mimics the speaker's style using prepared remarks as context
- Export options for speech and LLM prompt

### Desktop Application Interface (Legacy)
- **Two-Tab Popup Windows**: Dedicated windows showing prepared remarks and generated content
- **Streamlined 4-step workflow**: Upload → Speaker Name → Template → Custom Speech
- **Comprehensive Logging**: Detailed progress tracking with LLM prompt visibility

### Export Functionality
- **Web App**: Context-sensitive export buttons (Template/Speech/Remarks/Prompt)
- **Desktop App**: Separate export options from popup windows
- Files saved with speaker-specific naming convention

## Technical Architecture

### Project Structure
```
speech-writer/
├── web_app.py              # Flask web application (primary interface)
├── main.py                 # Tkinter desktop application (legacy)
├── templates/
│   └── index.html         # Web application HTML template
├── core/                   # Core functionality modules
│   ├── pdf_processor.py    # PDF text extraction & speaker identification
│   └── llm_providers.py    # Multi-provider AI integrations
├── utils/                  # Utility modules
│   ├── validators.py       # Input validation functions
│   └── logger.py          # Logging configuration
├── uploads/               # Temporary PDF storage directory
├── test_app.py            # Comprehensive test suite
├── test_pdf_replacement.py # PDF replacement workflow tests
├── requirements.txt        # Python dependencies
└── .env.example           # Environment variables template
```

### Core Components

#### PDF Processor
- **PyMuPDF Integration**: Robust text extraction from PDF files
- **LLM-Based Speaker Extraction**: AI-powered identification of prepared remarks
- **Content Validation**: Ensures sufficient speaker content for template generation
- **Smart Document Processing**: Leverages LLM understanding for accurate extraction

#### LLM Manager
- **Multi-Provider Support**: Unified interface for different AI services
- **Automatic Provider Detection**: Based on available API keys
- **Error Handling**: Comprehensive error reporting with detailed logging
- **Token Management**: Optimized prompts for template and speech generation

#### User Interface Frameworks
- **Flask Web Application**: Modern web-based interface with responsive design
  - Real-time status updates via AJAX polling
  - Responsive design for mobile and desktop
  - Context-sensitive export functionality
  - Threaded background processing
- **Tkinter Desktop Application (Legacy)**: Professional desktop interface
  - Popup-based results with tabbed interface
  - Non-blocking threaded operations
  - Comprehensive logging with LLM prompt visibility

## AI Provider Support

### Supported Providers
- **OpenAI**: GPT-3.5-turbo, GPT-4 series
- **Anthropic**: Claude-3-Sonnet, Claude-3-Haiku
- **Google**: Gemini-Pro
- **OpenRouter**: Multi-model access point

### Provider Features
- **Automatic Detection**: Based on configured API keys
- **Hot-swapping**: Change providers without restarting (web app) or via interface selection
- **Fallback Support**: Handles provider-specific errors gracefully
- **Custom Endpoints**: Support for OpenAI-compatible APIs

## Testing

### Main Test Suite
Run the comprehensive test suite:

```bash
python test_app.py
```

Tests validate:
- Module imports and dependencies
- PDF processing functionality
- LLM manager initialization
- Input validation functions
- Main application startup

### PDF Replacement Testing
Test PDF replacement workflow:

```bash
python test_pdf_replacement.py
```

Tests validate:
- PDF upload and replacement functionality
- Data clearing when new PDFs are selected
- Template generation workflow
- Application state management

## Troubleshooting

### Common Issues

1. **No AI providers available**
   - Verify API keys in `.env` file
   - Check API key format and validity
   - Ensure at least one provider is configured

2. **PDF processing fails**
   - Verify PDF is readable and not password-protected
   - Check file contains extractable text (not just images)
   - Ensure file path is accessible

3. **Speaker not found**
   - Check speaker name matches document format
   - Try variations: "John Smith" vs "Smith, John"
   - Verify speaker has sufficient content in document

4. **Generation errors**
   - Check API key validity and credits
   - Verify internet connectivity
   - Review logs for detailed error information

### Debug Information
- **Web Application**: Real-time status updates and error messages in browser interface
- **Desktop Application**: Application logs saved to `logs/speech_writer.log` with popup error messages
- Console output provides detailed error information for both interfaces
- Comprehensive test suites available: `python test_app.py` and `python test_pdf_replacement.py`

## Security Considerations

- **API Key Protection**: Environment variable storage only
- **Local Processing**: PDF analysis happens locally
- **No Data Persistence**: No sensitive information stored
- **Secure Connections**: HTTPS for all AI provider communications

## Deployment Options

### Local Development
```bash
python web_app.py
```
Access at `http://localhost:5000`

### Production Deployment
The Flask application supports production deployment with WSGI servers:

```bash
# Using Gunicorn (recommended)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web_app:app

# Environment variables for production
export FLASK_SECRET_KEY=your-production-secret-key
export PORT=5000  # Railway, Heroku, etc.
```

### Cloud Platform Deployment
- **Railway**: Automatic deployment with environment variable support
- **Heroku**: Compatible with Heroku's Python buildpack
- **Docker**: Containerization-ready Flask application

## Performance Optimization

- **Threaded Operations**: Background processing prevents interface blocking
- **Real-time Updates**: AJAX polling for status updates in web interface
- **Token Management**: Optimized prompts for efficiency across all providers
- **Memory Management**: Proper cleanup of large PDF content and temporary files
- **Error Recovery**: Graceful handling of provider failures with detailed feedback

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add comprehensive tests
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues, feature requests, and documentation:
- GitHub Issues: Report bugs and request features
- Test Suite: Verify functionality with `python test_app.py`
- **Web App**: Browser developer tools for client-side debugging
- **Desktop App**: Check `logs/speech_writer.log` for debugging