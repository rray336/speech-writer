"""
PDF Processing Module
Handles PDF text extraction and speaker content identification
"""

import fitz  # PyMuPDF
import re
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Handles PDF text extraction and processing for speech analysis"""
    
    def __init__(self, llm_manager=None):
        self.supported_formats = ['.pdf']
        self.llm_manager = llm_manager
    
    def extract_text_from_pdf(self, pdf_path: str) -> Dict:
        """
        Extract text from PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dict containing extracted text and metadata
        """
        try:
            doc = fitz.open(pdf_path)
            
            full_text = ""
            pages = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_text = page.get_text("text")
                pages.append({
                    "page_number": page_num + 1,
                    "text": page_text,
                    "char_count": len(page_text)
                })
                full_text += page_text + "\n"
            
            doc.close()
            
            return {
                "full_text": full_text,
                "pages": pages,
                "total_pages": len(pages),
                "total_chars": len(full_text),
                "metadata": {
                    "file_path": pdf_path,
                    "extraction_method": "PyMuPDF"
                }
            }
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF {pdf_path}: {e}")
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    
    
    
    def validate_pdf_file(self, file_path: str) -> Dict:
        """
        Validate PDF file and check if it can be processed
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dict containing validation results
        """
        try:
            # Check file exists and is readable
            import os
            if not os.path.exists(file_path):
                return {
                    "is_valid": False,
                    "error": "File does not exist",
                    "file_path": file_path
                }
            
            if not os.access(file_path, os.R_OK):
                return {
                    "is_valid": False,
                    "error": "File is not readable",
                    "file_path": file_path
                }
            
            # Try to open with PyMuPDF
            doc = fitz.open(file_path)
            page_count = len(doc)
            
            if page_count == 0:
                doc.close()
                return {
                    "is_valid": False,
                    "error": "PDF file contains no pages",
                    "file_path": file_path
                }
            
            # Try to extract text from first page
            first_page = doc.load_page(0)
            sample_text = first_page.get_text("text")
            doc.close()
            
            if len(sample_text.strip()) < 10:
                return {
                    "is_valid": False,
                    "error": "PDF appears to contain no extractable text (may be image-only)",
                    "file_path": file_path
                }
            
            return {
                "is_valid": True,
                "page_count": page_count,
                "sample_text_length": len(sample_text),
                "file_path": file_path,
                "file_size": os.path.getsize(file_path)
            }
            
        except Exception as e:
            return {
                "is_valid": False,
                "error": f"Error validating PDF: {str(e)}",
                "file_path": file_path
            }
    
    def extract_speaker_content_via_llm(self, full_text: str, speaker_name: str) -> Dict:
        """
        Extract speaker's prepared remarks using LLM
        
        Args:
            full_text: Complete PDF text
            speaker_name: Name of the speaker to extract content for
            
        Returns:
            Dict containing extracted speaker content and metadata
        """
        try:
            # Input validation
            if not self.llm_manager:
                raise Exception("LLM manager not available for speaker extraction")
            
            if not full_text or not full_text.strip():
                raise Exception("No text content provided for extraction")
            
            if not speaker_name or not speaker_name.strip():
                raise Exception("No speaker name provided. Please enter a speaker name.")
            
            speaker_name = speaker_name.strip()
            
            logger.info(f"Starting LLM-based extraction for speaker: {speaker_name}")
            
            # Use LLM to extract speaker content
            extracted_content = self.llm_manager.extract_speaker_prepared_remarks(full_text, speaker_name)
            
            # Validate LLM response
            if not extracted_content or not extracted_content.strip():
                raise Exception(f"LLM did not find any prepared remarks for speaker '{speaker_name}' in the document")
            
            extracted_content = extracted_content.strip()
            
            if len(extracted_content) < 50:
                raise Exception(f"LLM found insufficient content for speaker '{speaker_name}' (less than 50 characters)")
            
            logger.info(f"Successfully extracted {len(extracted_content)} characters of prepared remarks")
            
            return {
                "speaker_name": speaker_name,
                "content": extracted_content,
                "extraction_method": "llm",
                "content_length": len(extracted_content),
                "extraction_success": True,
                "content_type": "prepared_remarks"
            }
            
        except Exception as e:
            logger.error(f"LLM speaker extraction failed: {e}")
            return {
                "speaker_name": speaker_name,
                "content": "",
                "extraction_method": "failed",
                "content_length": 0,
                "extraction_success": False,
                "content_type": "prepared_remarks",
                "error": str(e)
            }