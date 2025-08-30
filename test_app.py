#!/usr/bin/env python3
"""
Test script for Speech Writer application
"""

import os
import sys
from pathlib import Path

def test_imports():
    """Test all module imports"""
    print("Testing module imports...")
    
    try:
        from core.pdf_processor import PDFProcessor
        print("[PASS] PDF processor imported successfully")
    except Exception as e:
        print(f"[FAIL] PDF processor import failed: {e}")
        return False
    
    try:
        from core.llm_providers import LLMManager
        print("[PASS] LLM providers imported successfully")
    except Exception as e:
        print(f"[FAIL] LLM providers import failed: {e}")
        return False
    
    try:
        from utils.validators import validate_pdf_file, validate_speaker_name, validate_key_messages
        print("[PASS] Validators imported successfully")
    except Exception as e:
        print(f"[FAIL] Validators import failed: {e}")
        return False
    
    return True

def test_pdf_processor():
    """Test PDF processor functionality"""
    print("\nTesting PDF processor...")
    
    try:
        from core.pdf_processor import PDFProcessor
        processor = PDFProcessor()
        
        # Test validation method
        validation = processor.validate_pdf_file("nonexistent.pdf")
        assert not validation["is_valid"]
        print("[PASS] PDF validation works for non-existent files")
        
        # Test LLM extraction method exists
        assert hasattr(processor, 'extract_speaker_content_via_llm')
        print("[PASS] LLM extraction method available")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] PDF processor test failed: {e}")
        return False

def test_llm_manager():
    """Test LLM manager functionality"""
    print("\nTesting LLM manager...")
    
    try:
        from core.llm_providers import LLMManager
        manager = LLMManager()
        
        # Test provider detection
        providers = manager.get_available_providers()
        print(f"Available providers: {providers}")
        
        if providers:
            # Test provider setting
            success = manager.set_provider(providers[0])
            assert success
            print(f"[PASS] Provider setting works ({providers[0]})")
        else:
            print("[INFO] No API keys configured - LLM functionality will be limited")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] LLM manager test failed: {e}")
        return False

def test_validators():
    """Test validation functions"""
    print("\nTesting validators...")
    
    try:
        from utils.validators import validate_pdf_file, validate_speaker_name, validate_key_messages
        
        # Test PDF validation
        result = validate_pdf_file("")
        assert not result["is_valid"]
        print("[PASS] PDF validation rejects empty path")
        
        result = validate_pdf_file("test.txt")
        assert not result["is_valid"]
        print("[PASS] PDF validation rejects non-PDF files")
        
        # Test speaker name validation
        result = validate_speaker_name("")
        assert not result["is_valid"]
        print("[PASS] Speaker validation rejects empty names")
        
        result = validate_speaker_name("John Doe")
        assert result["is_valid"]
        print("[PASS] Speaker validation accepts valid names")
        
        # Test key messages validation
        result = validate_key_messages("")
        assert not result["is_valid"]
        print("[PASS] Key messages validation rejects empty input")
        
        result = validate_key_messages("This is a valid message with enough content")
        assert result["is_valid"]
        print("[PASS] Key messages validation accepts valid input")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Validators test failed: {e}")
        return False

def test_main_app():
    """Test main application initialization"""
    print("\nTesting main application...")
    
    try:
        # Import without running GUI
        import tkinter as tk
        from main import SpeechWriterApp
        
        # Create root window (but don't show it)
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Initialize app
        app = SpeechWriterApp(root)
        
        # Test basic functionality
        assert hasattr(app, 'pdf_processor')
        assert hasattr(app, 'llm_manager')
        print("[PASS] Main application initializes successfully")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"[FAIL] Main application test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Speech Writer Application Tests")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_pdf_processor,
        test_llm_manager,
        test_validators,
        test_main_app
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"[FAIL] Test {test.__name__} crashed: {e}")
    
    print(f"\nTest Results: {passed}/{total} passed")
    
    if passed == total:
        print("[SUCCESS] All tests passed! The application should work correctly.")
        print("\nTo run the application:")
        print("python main.py")
    else:
        print("[WARNING] Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)