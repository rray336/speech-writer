"""
Validation utilities for Speech Writer
"""

import os
import re
from typing import Dict, Optional
from pathlib import Path

def validate_pdf_file(file_path: str) -> Dict:
    """
    Validate PDF file for speech analysis
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Dict with validation results
    """
    if not file_path or not file_path.strip():
        return {
            "is_valid": False,
            "error": "No file path provided"
        }
    
    # Check file existence
    if not os.path.exists(file_path):
        return {
            "is_valid": False,
            "error": f"File does not exist: {file_path}"
        }
    
    # Check file extension
    if not file_path.lower().endswith('.pdf'):
        return {
            "is_valid": False,
            "error": "File must be a PDF (.pdf extension)"
        }
    
    # Check file size (max 50MB)
    try:
        file_size = os.path.getsize(file_path)
        max_size = 50 * 1024 * 1024  # 50MB
        
        if file_size > max_size:
            return {
                "is_valid": False,
                "error": f"File too large ({file_size / (1024*1024):.1f}MB). Maximum size is 50MB."
            }
        
        if file_size == 0:
            return {
                "is_valid": False,
                "error": "File is empty"
            }
            
    except OSError as e:
        return {
            "is_valid": False,
            "error": f"Cannot access file: {str(e)}"
        }
    
    # Check file permissions
    if not os.access(file_path, os.R_OK):
        return {
            "is_valid": False,
            "error": "File is not readable. Check permissions."
        }
    
    return {
        "is_valid": True,
        "file_size": file_size,
        "file_path": file_path
    }

def validate_speaker_name(name: str) -> Dict:
    """
    Validate speaker name input
    
    Args:
        name: Speaker name to validate
        
    Returns:
        Dict with validation results
    """
    if not name or not name.strip():
        return {
            "is_valid": False,
            "error": "Speaker name cannot be empty"
        }
    
    cleaned_name = name.strip()
    
    # Check length
    if len(cleaned_name) < 2:
        return {
            "is_valid": False,
            "error": "Speaker name must be at least 2 characters long"
        }
    
    if len(cleaned_name) > 100:
        return {
            "is_valid": False,
            "error": "Speaker name too long (maximum 100 characters)"
        }
    
    # Check for valid characters (letters, spaces, hyphens, apostrophes, periods)
    if not re.match(r"^[a-zA-Z\s\-'.]+$", cleaned_name):
        return {
            "is_valid": False,
            "error": "Speaker name can only contain letters, spaces, hyphens, apostrophes, and periods"
        }
    
    # Check for reasonable structure (at least one letter)
    if not re.search(r'[a-zA-Z]', cleaned_name):
        return {
            "is_valid": False,
            "error": "Speaker name must contain at least one letter"
        }
    
    return {
        "is_valid": True,
        "cleaned_name": cleaned_name
    }

def validate_key_messages(messages: str) -> Dict:
    """
    Validate key messages input for custom speech generation
    
    Args:
        messages: Key messages text to validate
        
    Returns:
        Dict with validation results
    """
    if not messages or not messages.strip():
        return {
            "is_valid": False,
            "error": "Key messages cannot be empty"
        }
    
    cleaned_messages = messages.strip()
    
    # Check minimum length
    if len(cleaned_messages) < 10:
        return {
            "is_valid": False,
            "error": "Key messages must be at least 10 characters long"
        }
    
    # Check maximum length (10,000 characters to avoid token limits)
    if len(cleaned_messages) > 10000:
        return {
            "is_valid": False,
            "error": "Key messages too long (maximum 10,000 characters)"
        }
    
    # Check for meaningful content (not just whitespace or special characters)
    if not re.search(r'[a-zA-Z].*[a-zA-Z]', cleaned_messages):
        return {
            "is_valid": False,
            "error": "Key messages must contain meaningful text"
        }
    
    return {
        "is_valid": True,
        "cleaned_messages": cleaned_messages,
        "character_count": len(cleaned_messages)
    }

def validate_api_key(api_key: str, provider: str) -> Dict:
    """
    Validate API key format
    
    Args:
        api_key: API key to validate
        provider: Provider name (openai, claude, gemini, etc.)
        
    Returns:
        Dict with validation results
    """
    if not api_key or not api_key.strip():
        return {
            "is_valid": False,
            "error": f"No API key provided for {provider}"
        }
    
    cleaned_key = api_key.strip()
    
    # Basic length checks by provider
    min_lengths = {
        "openai": 40,      # OpenAI keys are typically 51 characters
        "claude": 40,      # Claude keys vary but are substantial
        "gemini": 30,      # Google API keys
        "openrouter": 40   # OpenRouter keys
    }
    
    min_length = min_lengths.get(provider.lower(), 20)  # Default minimum
    
    if len(cleaned_key) < min_length:
        return {
            "is_valid": False,
            "error": f"API key for {provider} appears too short (minimum {min_length} characters)"
        }
    
    # Check for obvious invalid formats
    if cleaned_key in ["demo", "test", "placeholder", "your_api_key_here"]:
        return {
            "is_valid": False,
            "error": f"Please provide a valid API key for {provider}"
        }
    
    # Provider-specific format checks
    if provider.lower() == "openai":
        if not cleaned_key.startswith("sk-"):
            return {
                "is_valid": False,
                "error": "OpenAI API keys should start with 'sk-'"
            }
    
    return {
        "is_valid": True,
        "provider": provider
    }

def validate_file_path(file_path: str, allowed_extensions: list = None) -> Dict:
    """
    Generic file path validation
    
    Args:
        file_path: Path to validate
        allowed_extensions: List of allowed file extensions (with dots)
        
    Returns:
        Dict with validation results
    """
    if not file_path or not file_path.strip():
        return {
            "is_valid": False,
            "error": "No file path provided"
        }
    
    path = Path(file_path)
    
    # Check if file exists
    if not path.exists():
        return {
            "is_valid": False,
            "error": f"File does not exist: {file_path}"
        }
    
    # Check if it's a file (not directory)
    if not path.is_file():
        return {
            "is_valid": False,
            "error": f"Path is not a file: {file_path}"
        }
    
    # Check file extension if specified
    if allowed_extensions:
        file_ext = path.suffix.lower()
        allowed_lower = [ext.lower() for ext in allowed_extensions]
        
        if file_ext not in allowed_lower:
            return {
                "is_valid": False,
                "error": f"Invalid file type. Allowed extensions: {', '.join(allowed_extensions)}"
            }
    
    return {
        "is_valid": True,
        "file_path": str(path.absolute()),
        "file_name": path.name,
        "file_extension": path.suffix
    }