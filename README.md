# Speech Writer

AI-powered speech template and speech generator built with Python and Tkinter. Extracts speaker-specific prepared remarks from PDF transcripts and generates personalized templates and speeches with sophisticated popup-based interface.

## Features

### Core Functionality
- **LLM-Powered PDF Analysis**: AI extracts and identifies speaker-specific prepared remarks from transcripts
- **Direct Template Generation**: Creates structured speech templates directly from prepared remarks
- **Custom Speech Generation**: Converts key messages into full speeches using prepared remarks as style context
- **Multi-Provider AI Support**: OpenAI, Claude, Gemini, and OpenRouter integration

### User Interface
- **Professional Desktop GUI**: Clean Tkinter interface with streamlined 4-step workflow
- **Popup-Based Results**: Dedicated windows for templates and speeches with tabbed interface
- **Real-time Processing**: Threaded operations prevent GUI freezing
- **Comprehensive Logging**: Detailed progress tracking and LLM prompt visibility
- **Export Functionality**: Save prepared remarks, templates, and speeches from popup windows

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
   ```bash
   python main.py
   ```

### System Requirements
- Python 3.8 or higher
- Windows/macOS/Linux with GUI support
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

### Step 1: Upload PDF Transcript
- Click "Browse" to select a PDF file containing speaker transcripts
- Supports transcripts with multiple speakers, Q&A sessions, prepared remarks
- Application validates file format and readability

### Step 2: Enter speaker name (e.g., David)
- Enter the exact name of the speaker you want to extract content for
- Name matching is case-insensitive and flexible (supports variations)

### Step 3: Generate Template
- Click "Generate Template" to extract prepared remarks and create speech template
- **Two-Tab Popup Window** displays:
  - **Tab 1**: LLM-extracted prepared remarks from the PDF
  - **Tab 2**: Generated speech template with structured bullet points
- Template summarizes prepared remarks in presentation-ready format

### Step 4: Generate Custom Speech
- Enter your key messages in the text area
- Click "Generate Custom Speech" for full speech conversion
- **Speech Popup Window**: Shows complete speech that mimics the speaker's style using prepared remarks as context

### Export Results
- Template window: Export prepared remarks or template separately
- Speech window: Export complete speech
- Files saved with speaker-specific naming

## Technical Architecture

### Project Structure
```
speech-writer/
├── main.py                 # Main GUI application (750+ lines)
├── core/                   # Core functionality modules
│   ├── pdf_processor.py    # PDF text extraction & speaker identification
│   └── llm_providers.py    # Multi-provider AI integrations
├── utils/                  # Utility modules
│   ├── validators.py       # Input validation functions
│   └── logger.py          # Logging configuration
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

#### GUI Framework
- **Tkinter-based Interface**: Professional desktop application with streamlined workflow
- **Threaded Processing**: Non-blocking operations for better UX
- **Tabbed Popup Windows**: Dedicated windows showing prepared remarks and generated content
- **Progress Tracking**: Real-time status updates and comprehensive logging with LLM prompt visibility

## AI Provider Support

### Supported Providers
- **OpenAI**: GPT-3.5-turbo, GPT-4 series
- **Anthropic**: Claude-3-Sonnet, Claude-3-Haiku
- **Google**: Gemini-Pro
- **OpenRouter**: Multi-model access point

### Provider Features
- **Automatic Detection**: Based on configured API keys
- **Hot-swapping**: Change providers without restarting
- **Fallback Support**: Handles provider-specific errors
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
- Application logs saved to `logs/speech_writer.log`
- Popup windows show detailed error messages
- Main interface displays real-time processing status
- Comprehensive test suites available: `python test_app.py` and `python test_pdf_replacement.py`

## Security Considerations

- **API Key Protection**: Environment variable storage only
- **Local Processing**: PDF analysis happens locally
- **No Data Persistence**: No sensitive information stored
- **Secure Connections**: HTTPS for all AI provider communications

## Performance Optimization

- **Threaded Operations**: Prevent GUI blocking during processing
- **Token Management**: Optimized prompts for efficiency
- **Memory Management**: Proper cleanup of large PDF content
- **Error Recovery**: Graceful handling of provider failures

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
- Logs: Check `logs/speech_writer.log` for debugging