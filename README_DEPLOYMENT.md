# Speech Writer - Railway Deployment Guide

## Overview

This guide covers deploying the Speech Writer application to Railway as a web service. The application has been converted from a desktop GUI app to a Flask web application for cloud deployment.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Code must be pushed to GitHub
3. **Environment Variables**: API keys for AI providers

## Required Environment Variables

Set these in your Railway project dashboard:

```bash
# Required: At least one AI provider API key
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Optional: Flask secret key (Railway will generate one if not provided)
FLASK_SECRET_KEY=your_secret_key_here
```

## Deployment Steps

### 1. Prepare Your Repository

Ensure your repository contains:

- ✅ `web_app.py` - Flask web server
- ✅ `requirements.txt` - Python dependencies including Flask and gunicorn
- ✅ `Procfile` - Railway deployment configuration
- ✅ `templates/index.html` - Web interface
- ✅ `.gitignore` - Excludes sensitive files and uploads directory

### 2. Deploy to Railway

1. **Connect Repository**:

   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your speech-writer repository

2. **Configure Environment Variables**:

   - In Railway dashboard, go to your project
   - Click "Variables" tab
   - Add the required environment variables listed above

3. **Deploy**:
   - Railway will automatically detect the `Procfile`
   - The build process will install dependencies from `requirements.txt`
   - The app will start using: `gunicorn web_app:app`

### 3. Access Your Application

Once deployed, Railway will provide a URL like:
`https://your-app-name.railway.app`

## Application Features

The web version maintains all core functionality from the desktop app:

### Step 1: Upload PDF Transcript

- Upload PDF files up to 16MB
- Automatic validation and text extraction

### Step 2: Enter Speaker Name

- Specify the speaker whose content you want to analyze

### Step 3: Generate Template

- AI-powered extraction of speaker's prepared remarks
- Generation of speech template based on speaking style

### Step 4: Custom Speech Generation

- Input key messages
- Generate custom speech in the speaker's style
- Uses prepared remarks as context for style consistency

### Export Options

- Export templates, speeches, prepared remarks, and LLM prompts
- Download as text files

## File Structure

```
speech-writer/
├── web_app.py              # Flask web server
├── main.py                 # Original desktop app (still functional)
├── Procfile                # Railway deployment config
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html         # Web interface
├── core/
│   ├── pdf_processor.py   # PDF processing logic
│   └── llm_providers.py   # AI provider integrations
├── utils/
│   ├── validators.py      # Input validation
│   └── logger.py          # Logging utilities
└── memory-bank/           # Project documentation
```

## Local Testing

To test the web app locally before deployment:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables (create .env file)
cp .env.example .env
# Edit .env with your API keys

# Run the web app
python web_app.py
```

Visit http://localhost:5000 to test the application.

## Production Considerations

### Security

- Environment variables are used for all sensitive data
- File uploads are validated and stored temporarily
- Uploaded files are cleaned up after processing

### Performance

- Background threading for long-running AI operations
- Asynchronous status updates via AJAX
- Efficient file handling with automatic cleanup

### Monitoring

- Server logs available in Railway dashboard
- Error handling with user-friendly messages
- Status tracking for all operations

## Troubleshooting

### Common Issues

1. **No AI providers available**:

   - Check that at least one API key is set in Railway environment variables
   - Verify API key format and validity

2. **File upload errors**:

   - Ensure PDF files are under 16MB
   - Check file format is valid PDF

3. **Processing timeouts**:
   - Large PDFs may take longer to process
   - Check Railway logs for detailed error messages

### Railway Logs

Access logs in Railway dashboard:

1. Go to your project
2. Click "Deployments" tab
3. Click on latest deployment
4. View "Logs" section

## Support

For issues specific to:

- **Railway deployment**: Check Railway documentation
- **Application functionality**: Review the original desktop app documentation
- **API integrations**: Verify API key configuration and provider status

## Migration from Desktop App

The web version maintains the same core functionality as the desktop app (`main.py`). Key differences:

- **Interface**: Web-based instead of Tkinter GUI
- **File handling**: Temporary uploads instead of file browser
- **Processing**: Background threads with status updates
- **Export**: Direct download instead of save dialog

Both versions can coexist and use the same core processing modules.
