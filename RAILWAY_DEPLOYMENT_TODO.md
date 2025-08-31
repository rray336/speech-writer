# Railway Deployment Todo List

## Project: Speech Writer Web App Deployment

### Phase 1: Web Framework Setup

- [x] Add Flask and related dependencies to requirements.txt
- [x] Create a new Flask web server file (web_app.py)
- [x] Create basic HTML templates for web interface

### Phase 2: Core Functionality Integration

- [x] Wrap core functionality from main.py into Flask routes:
  - [x] Route for uploading PDF transcripts
  - [x] Route for entering speaker name and generating templates
  - [x] Route for custom speech generation
- [x] Implement file upload handling and storage for PDF files
- [x] Implement API endpoints to trigger PDF processing and LLM calls
- [x] Handle asynchronous processing for long-running LLM operations

### Phase 3: Web Interface

- [x] Create simple HTML templates or use JSON responses for frontend interaction
- [x] Implement file upload form
- [x] Create speaker name input form
- [x] Display generated templates and speeches
- [x] Add export functionality for generated content

### Phase 4: Railway Deployment Configuration

- [x] Add Railway-specific deployment files:
  - [x] Procfile specifying the web process
  - [x] railway.toml configuration (if needed)
- [x] Modify app to read PORT environment variable for server binding
- [x] Ensure environment variables are properly configured for Railway
- [x] Update .gitignore to exclude sensitive files

### Phase 5: Testing and Documentation

- [x] Test the Flask app locally to ensure all functionality works via HTTP
- [ ] Test file upload and processing workflows
- [ ] Verify all LLM integrations work in web environment
- [x] Update README with deployment and usage instructions for Railway
- [x] Document API endpoints and usage

### Phase 6: Deployment

- [ ] Commit all changes and push to GitHub repository
- [ ] Connect GitHub repository to Railway
- [ ] Configure environment variables in Railway dashboard
- [ ] Deploy and test in production environment
- [ ] Monitor logs and fix any deployment issues

## Notes

- Using Flask as the web framework (simpler than FastAPI for this use case)
- Maintaining existing core functionality from desktop app
- Following custom instructions for git-ignore rules and memory bank updates
