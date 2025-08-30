# Installation Guide

## System Requirements

### Minimum Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows 10+, macOS 10.14+, or Linux with GUI support
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 100MB for application, additional space for logs and exports
- **Network**: Internet connection for AI provider APIs

### Recommended Requirements
- **Python**: 3.11+ for best performance
- **Memory**: 8GB+ RAM for processing large PDF files
- **Display**: 1024x768 minimum resolution, 1200x800+ recommended for optimal UI experience

## Installation Steps

### 1. Python Environment Setup

#### Option A: System Python (Recommended for most users)
```bash
# Verify Python version
python --version  # Should be 3.8+

# Install the application
pip install -r requirements.txt
```

#### Option B: Virtual Environment (Recommended for developers)
```bash
# Create virtual environment
python -m venv speech-writer-env

# Activate virtual environment
# Windows:
speech-writer-env\Scripts\activate
# macOS/Linux:
source speech-writer-env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Dependency Installation

The following packages will be installed:

#### Core Dependencies
- **PyMuPDF** (≥1.23.0): PDF text extraction
- **python-dotenv** (≥1.0.0): Environment variable management
- **requests** (≥2.31.0): HTTP client for AI APIs

#### AI Provider Dependencies
- **openai** (≥1.0.0): OpenAI GPT models
- **anthropic** (≥0.7.0): Claude models
- **google-generativeai** (≥0.3.0): Gemini models

#### Optional Dependencies
- **colorlog** (≥6.7.0): Colored logging output
- **tqdm** (≥4.66.0): Progress bars (for future enhancements)

### 3. Configuration Setup

#### Environment Variables
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your preferred text editor
# Add at least one AI provider API key
```

#### Required API Keys (Choose at least one)
- **OpenAI**: Get from https://platform.openai.com/api-keys
- **Anthropic (Claude)**: Get from https://console.anthropic.com/
- **Google (Gemini)**: Get from https://makersuite.google.com/app/apikey
- **OpenRouter**: Get from https://openrouter.ai/keys

### 4. Verification

#### Run Test Suite
```bash
# Run main application tests
python test_app.py

# Run PDF replacement workflow tests
python test_pdf_replacement.py
```

Expected output for main tests:
```
Speech Writer Application Tests
========================================
[PASS] PDF processor imported successfully
[PASS] LLM providers imported successfully
[PASS] Validators imported successfully
[PASS] PDF validation works
[PASS] LLM manager initialization
[PASS] Main application initializes successfully

Test Results: 5/5 passed
[SUCCESS] All tests passed!
```

#### Launch Application
```bash
python main.py
```

## Troubleshooting Installation

### Common Issues

#### 1. Python Version Issues
```bash
# Error: Python version too old
# Solution: Install Python 3.8+
python --version  # Check current version
```

#### 2. Permission Issues (Windows)
```bash
# Error: Permission denied during pip install
# Solution: Run as administrator or use --user flag
pip install --user -r requirements.txt
```

#### 3. Permission Issues (macOS/Linux)
```bash
# Error: Permission denied during pip install
# Solution: Use user installation
pip install --user -r requirements.txt
```

#### 4. GUI Dependencies (Linux)
```bash
# Error: No module named '_tkinter'
# Solution: Install tkinter
sudo apt-get install python3-tk  # Ubuntu/Debian
sudo yum install tkinter         # CentOS/RHEL
```

#### 5. PDF Processing Issues
```bash
# Error: PyMuPDF installation failed
# Solution: Install system dependencies
# Windows: Usually works with pip
# macOS: May need Xcode command line tools
xcode-select --install

# Linux: Install development headers
sudo apt-get install python3-dev  # Ubuntu/Debian
```

### Platform-Specific Notes

#### Windows
- Windows Defender may flag the application initially
- Use PowerShell or Command Prompt for installation
- GUI scaling may affect window layouts on high-DPI displays

#### macOS
- May need to allow the application in System Preferences > Security & Privacy
- Xcode command line tools required for some dependencies
- Application appears in Dock when running

#### Linux
- Requires X11 or Wayland display server
- Some distributions may need additional GUI libraries
- Font rendering may vary by desktop environment

## Development Setup

### Additional Development Dependencies
```bash
# Install development tools
pip install pytest black flake8

# Run code formatting
black main.py core/ utils/

# Run linting
flake8 main.py core/ utils/

# Run tests with coverage
python test_app.py
```

### IDE Configuration

#### VS Code
Recommended extensions:
- Python
- Python Docstring Generator
- Black Formatter

#### PyCharm
- Configure Python interpreter to project virtual environment
- Enable code formatting on save
- Set up run configurations for main.py and test_app.py

## Advanced Configuration

### Custom AI Endpoints
```env
# .env file
OPENAI_BASE_URL=https://your-custom-endpoint.com/v1
OPENROUTER_BASE_URL=https://your-proxy.com/v1
```

### Logging Configuration
```python
# Modify utils/logger.py for custom log levels
LOG_LEVEL=DEBUG  # For verbose logging
LOG_LEVEL=INFO   # Default
LOG_LEVEL=ERROR  # Minimal logging
```

### Performance Tuning
```env
# .env file additions for performance
TIMEOUT=60      # API timeout in seconds
MAX_RETRIES=3   # Number of retry attempts
```

## Uninstallation

### Remove Application
```bash
# If using virtual environment
deactivate
rm -rf speech-writer-env/

# If using system Python
pip uninstall -r requirements.txt

# Remove application files
rm -rf speech-writer/
```

### Clean up
```bash
# Remove logs and temporary files
rm -rf logs/
rm -rf __pycache__/
```

## Getting Help

### Support Channels
1. **Test Suites**: Run `python test_app.py` and `python test_pdf_replacement.py` to verify installation
2. **Log Files**: Check `logs/speech_writer.log` for detailed errors  
3. **GitHub Issues**: Report installation problems with system details
4. **Documentation**: Review README.md for usage instructions

### System Information for Bug Reports
```bash
# Gather system information for bug reports
python --version
pip list | grep -E "(PyMuPDF|openai|anthropic|google-generativeai)"
```

Include this information when reporting installation issues.