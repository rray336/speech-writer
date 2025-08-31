#!/usr/bin/env python3
"""
Speech Writer Web App - Flask Web Server
AI-powered speech style analyzer and generator for web deployment
"""

import os
import json
import threading
from pathlib import Path
from typing import Optional, Dict, Any
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from flask import Flask, request, render_template, jsonify, redirect, url_for, flash, send_file
from werkzeug.datastructures import FileStorage

# Import our custom modules
from core.pdf_processor import PDFProcessor
from core.llm_providers import LLMManager
from utils.validators import validate_pdf_file, validate_speaker_name, validate_key_messages

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global variables for processing state
processing_state = {
    'is_processing': False,
    'current_task': None,
    'progress': 'Ready',
    'transcript_text': None,
    'speaker_content': None,
    'current_speaker_name': None,
    'generated_template': None,  # Store template separately
    'generated_speech': None,    # Store custom speech separately
    'generated_prompt': None,    # Store LLM prompt
    'error_message': None,
    'current_phase': 'initial'   # Track current phase: 'initial', 'template', 'speech'
}

# Initialize processors
llm_manager = None
pdf_processor = None

def initialize_processors():
    """Initialize LLM manager and PDF processor"""
    global llm_manager, pdf_processor
    
    try:
        # Debug: Print environment variables
        print("DEBUG: Checking environment variables:")
        for key in ['OPENAI_API_KEY', 'CLAUDE_API_KEY', 'GEMINI_API_KEY', 'OPENROUTER_API_KEY']:
            val = os.getenv(key)
            print(f"  {key}: {'Set' if val else 'Not set'}")
        
        # Initialize LLM manager first
        llm_manager = LLMManager()
        available_providers = llm_manager.get_available_providers()
        
        if not available_providers:
            print("WARNING: No AI provider API keys found. Please configure your .env file.")
            print("See .env.example for required environment variables.")
            # Initialize PDF processor without LLM manager
            pdf_processor = PDFProcessor()
            return False
        else:
            print(f"Available AI providers: {', '.join(available_providers)}")
            
            # Set to first available provider
            llm_manager.set_provider(available_providers[0])
            
            # Initialize PDF processor with LLM manager
            pdf_processor = PDFProcessor(llm_manager)
            return True
            
    except Exception as e:
        print(f"ERROR: Failed to initialize processors: {e}")
        import traceback
        traceback.print_exc()
        return False

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html', 
                         processing_state=processing_state,
                         available_providers=llm_manager.get_available_providers() if llm_manager else [])

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle PDF file upload"""
    global processing_state
    
    # Reset processing state for new upload
    processing_state.update({
        'transcript_text': None,
        'speaker_content': None,
        'current_speaker_name': None,
        'generated_template': None,
        'generated_speech': None,
        'generated_prompt': None,
        'error_message': None,
        'progress': 'Ready',
        'current_phase': 'initial'
    })
    
    if 'pdf_file' not in request.files:
        flash('No file selected')
        return redirect(url_for('index'))
    
    file = request.files['pdf_file']
    
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Validate the uploaded file
        pdf_validation = validate_pdf_file(filepath)
        if not pdf_validation["is_valid"]:
            flash(f'Invalid PDF file: {pdf_validation["error"]}')
            os.remove(filepath)  # Clean up invalid file
            return redirect(url_for('index'))
        
        processing_state['uploaded_file'] = filepath
        flash(f'File uploaded successfully: {filename}')
        return redirect(url_for('index'))
    else:
        flash('Invalid file type. Please upload a PDF file.')
        return redirect(url_for('index'))

@app.route('/set_provider', methods=['POST'])
def set_provider():
    """Set AI provider"""
    global llm_manager
    
    if not llm_manager:
        return jsonify({'error': 'AI services not available'}), 500
    
    provider = request.form.get('provider', '').strip()
    available_providers = llm_manager.get_available_providers()
    
    if provider not in available_providers:
        return jsonify({'error': f'Provider {provider} not available. Available: {available_providers}'}), 400
    
    success = llm_manager.set_provider(provider)
    if success:
        return jsonify({'message': f'AI provider switched to: {provider}', 'current_provider': provider})
    else:
        return jsonify({'error': f'Failed to switch to provider: {provider}'}), 500

@app.route('/generate_template', methods=['POST'])
def generate_template():
    """Generate speech template"""
    global processing_state
    
    if not pdf_processor or not llm_manager:
        return jsonify({'error': 'AI services not available. Please configure API keys.'}), 500
    
    if processing_state['is_processing']:
        return jsonify({'error': 'Another operation is in progress'}), 400
    
    # Get form data
    speaker_name = request.form.get('speaker_name', '').strip()
    
    # Validate inputs
    if 'uploaded_file' not in processing_state:
        return jsonify({'error': 'Please upload a PDF file first'}), 400
    
    name_validation = validate_speaker_name(speaker_name)
    if not name_validation["is_valid"]:
        return jsonify({'error': name_validation["error"]}), 400
    
    # Start processing in background thread
    def process_template():
        global processing_state
        
        try:
            processing_state.update({
                'is_processing': True,
                'current_task': 'template_generation',
                'progress': 'Processing PDF...',
                'error_message': None
            })
            
            pdf_file = processing_state['uploaded_file']
            
            # Extract text from PDF
            print(f"Extracting text from: {os.path.basename(pdf_file)}")
            pdf_data = pdf_processor.extract_text_from_pdf(pdf_file)
            processing_state['transcript_text'] = pdf_data["full_text"]
            
            processing_state['progress'] = 'Extracting speaker prepared remarks...'
            
            # Extract speaker content using LLM
            print(f"Extracting prepared remarks for speaker: {speaker_name}")
            speaker_data = pdf_processor.extract_speaker_content_via_llm(
                processing_state['transcript_text'], speaker_name
            )
            
            if not speaker_data["extraction_success"]:
                raise Exception(speaker_data.get("error", f"Could not extract prepared remarks for speaker '{speaker_name}'"))
            
            processing_state['speaker_content'] = speaker_data["content"]
            print(f"Extracted {len(processing_state['speaker_content'])} characters of prepared remarks")
            
            processing_state['progress'] = 'Generating template...'
            
            # Generate template using LLM
            print("Generating speech template...")
            template = llm_manager.generate_template(processing_state['speaker_content'], speaker_name)
            
            processing_state.update({
                'generated_template': template,
                'current_speaker_name': speaker_name,
                'progress': 'Template generated successfully',
                'is_processing': False,
                'current_task': None,
                'current_phase': 'template'
            })
            
        except Exception as e:
            processing_state.update({
                'error_message': str(e),
                'progress': 'Error occurred',
                'is_processing': False,
                'current_task': None
            })
            print(f"ERROR: Template generation failed - {e}")
    
    # Start background thread
    thread = threading.Thread(target=process_template)
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': 'Template generation started', 'status': 'processing'})

@app.route('/generate_speech', methods=['POST'])
def generate_speech():
    """Generate custom speech from key messages"""
    global processing_state
    
    if not pdf_processor or not llm_manager:
        return jsonify({'error': 'AI services not available. Please configure API keys.'}), 500
    
    if processing_state['is_processing']:
        return jsonify({'error': 'Another operation is in progress'}), 400
    
    if not processing_state['speaker_content']:
        return jsonify({'error': 'Please generate template first to extract prepared remarks'}), 400
    
    # Get form data
    key_messages = request.form.get('key_messages', '').strip()
    speaker_name = processing_state.get('current_speaker_name', '')
    
    # Validate inputs
    messages_validation = validate_key_messages(key_messages)
    if not messages_validation["is_valid"]:
        return jsonify({'error': messages_validation["error"]}), 400
    
    if not speaker_name:
        return jsonify({'error': 'Speaker name not available. Please generate template first.'}), 400
    
    # Start processing in background thread
    def process_speech():
        global processing_state
        
        try:
            processing_state.update({
                'is_processing': True,
                'current_task': 'speech_generation',
                'progress': 'Generating custom speech...',
                'error_message': None
            })
            
            # Generate custom speech using LLM
            print("Generating custom speech from key messages...")
            speech, prompt = llm_manager.generate_custom_speech(
                processing_state['speaker_content'],
                key_messages,
                speaker_name
            )
            
            processing_state.update({
                'generated_speech': speech,
                'generated_prompt': prompt,
                'progress': 'Custom speech generated successfully',
                'is_processing': False,
                'current_task': None,
                'current_phase': 'speech'
            })
            
        except Exception as e:
            processing_state.update({
                'error_message': str(e),
                'progress': 'Error occurred',
                'is_processing': False,
                'current_task': None
            })
            print(f"ERROR: Speech generation failed - {e}")
    
    # Start background thread
    thread = threading.Thread(target=process_speech)
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': 'Speech generation started', 'status': 'processing'})

@app.route('/status')
def get_status():
    """Get current processing status"""
    return jsonify({
        'is_processing': processing_state['is_processing'],
        'current_task': processing_state['current_task'],
        'progress': processing_state['progress'],
        'error_message': processing_state['error_message'],
        'has_template': processing_state['generated_template'] is not None,
        'has_speech': processing_state['generated_speech'] is not None,
        'has_speaker_content': processing_state['speaker_content'] is not None,
        'has_prompt': processing_state['generated_prompt'] is not None,
        'current_phase': processing_state['current_phase'],
        'speaker_name': processing_state.get('current_speaker_name', '')
    })

@app.route('/results')
def get_results():
    """Get generated results"""
    current_phase = processing_state['current_phase']
    
    if current_phase == 'template' and processing_state['generated_template']:
        generated_output = processing_state['generated_template']
    elif current_phase == 'speech' and processing_state['generated_speech']:
        generated_output = processing_state['generated_speech']
    else:
        return jsonify({'error': 'No results available'}), 404
    
    return jsonify({
        'generated_output': generated_output,
        'speaker_content': processing_state['speaker_content'],
        'speaker_name': processing_state.get('current_speaker_name', ''),
        'generated_prompt': processing_state.get('generated_prompt', ''),
        'current_phase': current_phase
    })

@app.route('/export/<content_type>')
def export_content(content_type):
    """Export content as text file"""
    if content_type not in ['template', 'speech', 'remarks', 'prompt']:
        return jsonify({'error': 'Invalid content type'}), 400
    
    speaker_name = processing_state.get('current_speaker_name', 'Speaker')
    
    if content_type == 'template' and processing_state['generated_template']:
        content = f"SPEECH TEMPLATE\nSpeaker: {speaker_name}\n{'='*60}\n\n{processing_state['generated_template']}"
        filename = f"{speaker_name}_template.txt"
    elif content_type == 'speech' and processing_state['generated_speech']:
        content = f"CUSTOM SPEECH\nSpeaker: {speaker_name}\n{'='*60}\n\n{processing_state['generated_speech']}"
        filename = f"{speaker_name}_speech.txt"
    elif content_type == 'remarks' and processing_state['speaker_content']:
        content = f"PREPARED REMARKS\nSpeaker: {speaker_name}\n{'='*60}\n\n{processing_state['speaker_content']}"
        filename = f"{speaker_name}_remarks.txt"
    elif content_type == 'prompt' and processing_state.get('generated_prompt'):
        content = f"LLM PROMPT\nSpeaker: {speaker_name}\n{'='*60}\n\n{processing_state['generated_prompt']}"
        filename = f"{speaker_name}_prompt.txt"
    else:
        return jsonify({'error': 'Content not available'}), 404
    
    # Create temporary file
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return send_file(temp_path, as_attachment=True, download_name=filename)

@app.route('/reset', methods=['POST'])
def reset_app():
    """Reset application state"""
    global processing_state
    
    # Clean up uploaded files
    if 'uploaded_file' in processing_state and os.path.exists(processing_state['uploaded_file']):
        try:
            os.remove(processing_state['uploaded_file'])
        except:
            pass
    
    # Reset state
    processing_state.update({
        'is_processing': False,
        'current_task': None,
        'progress': 'Ready',
        'transcript_text': None,
        'speaker_content': None,
        'current_speaker_name': None,
        'generated_output': None,
        'generated_prompt': None,
        'error_message': None,
        'uploaded_file': None
    })
    
    flash('Application reset successfully')
    return redirect(url_for('index'))

# Initialize processors when module is loaded (works with both direct run and gunicorn)
processors_initialized = initialize_processors()

if not processors_initialized:
    print("WARNING: Running with limited functionality due to missing API keys")

if __name__ == '__main__':
    # Get port from environment variable (Railway sets this)
    port = int(os.environ.get('PORT', 5000))
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=False)
