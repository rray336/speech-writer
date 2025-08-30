#!/usr/bin/env python3
"""
Speech Writer App - Main GUI Application
AI-powered speech style analyzer and generator
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
from pathlib import Path
import json
import threading
from typing import List, Optional
from dotenv import load_dotenv

# Import our custom modules
from core.pdf_processor import PDFProcessor
from core.llm_providers import LLMManager
from utils.validators import validate_pdf_file, validate_speaker_name, validate_key_messages

# Load environment variables
load_dotenv()

class SpeechWriterApp:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_variables()
        self.create_widgets()
        self.initialize_processors()
        
    def setup_window(self):
        """Set up the main window"""
        self.root.title("Speech Writer - AI-Powered Style Analysis")
        self.root.geometry("1000x620")
        self.root.minsize(800, 600)
        
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.root.winfo_screenheight() // 2) - (620 // 2)
        self.root.geometry(f"1000x620+{x}+{y}")
    
    def setup_variables(self):
        """Set up tkinter variables"""
        self.llm_provider_var = tk.StringVar(value="openai")
        self.generation_mode_var = tk.StringVar(value="template")
        self.speaker_name_var = tk.StringVar()
        
        # File variables
        self.pdf_file_var = tk.StringVar()
        
        # Analysis results storage
        self.transcript_text = None
        self.speaker_content = None
        self.current_speaker_name = None
        self.generated_output = None
        
        # Processing states
        self.is_processing = False
        
    def create_widgets(self):
        """Create all GUI widgets"""
        # Create main frames
        self.create_header_frame()
        self.create_file_input_frame()
        self.create_speaker_frame()
        self.create_generation_frame()
        self.create_custom_speech_frame()
        self.create_controls_frame()
        self.create_progress_frame()
        self.create_log_frame()
    
    def create_header_frame(self):
        """Create header with title and settings"""
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        # Title
        title_label = ttk.Label(header_frame, text="Speech Writer", 
                               font=("Arial", 16, "bold"))
        title_label.pack(side="left")
        
        subtitle_label = ttk.Label(header_frame, text="AI-Powered Speech Style Analysis & Generation",
                                  font=("Arial", 10), foreground="gray")
        subtitle_label.pack(side="left", padx=(10, 0))
        
        # LLM Provider selection
        provider_frame = ttk.Frame(header_frame)
        provider_frame.pack(side="right")
        
        ttk.Label(provider_frame, text="AI Provider:").pack(side="left", padx=(0, 5))
        provider_combo = ttk.Combobox(provider_frame, textvariable=self.llm_provider_var,
                                     values=["openai", "claude", "gemini", "openrouter"],
                                     state="readonly", width=12)
        provider_combo.pack(side="left")
        provider_combo.bind("<<ComboboxSelected>>", self.on_provider_change)
    
    def create_file_input_frame(self):
        """Create PDF file input frame"""
        file_frame = ttk.LabelFrame(self.root, text="Step 1: Upload PDF Transcript")
        file_frame.pack(fill="x", padx=10, pady=5)
        
        input_frame = ttk.Frame(file_frame)
        input_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(input_frame, text="PDF File:").pack(side="left")
        
        file_entry = ttk.Entry(input_frame, textvariable=self.pdf_file_var, state="readonly")
        file_entry.pack(side="left", fill="x", expand=True, padx=(10, 5))
        
        browse_button = ttk.Button(input_frame, text="Browse", command=self.browse_pdf_file)
        browse_button.pack(side="right")
        
    
    def create_speaker_frame(self):
        """Create speaker identification frame"""
        speaker_frame = ttk.LabelFrame(self.root, text="Step 2: Enter speaker name (e.g., David)")
        speaker_frame.pack(fill="x", padx=10, pady=5)
        
        input_frame = ttk.Frame(speaker_frame)
        input_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(input_frame, text="Speaker Name:").pack(side="left")
        
        speaker_entry = ttk.Entry(input_frame, textvariable=self.speaker_name_var)
        speaker_entry.pack(side="left", fill="x", expand=True, padx=(10, 5))
        
        
    
    
    def create_generation_frame(self):
        """Create generation input frame"""
        self.gen_frame = ttk.LabelFrame(self.root, text="Step 3: Generate Template")
        self.gen_frame.pack(fill="x", padx=10, pady=5)
        
        # Template generation section
        template_frame = ttk.Frame(self.gen_frame)
        template_frame.pack(fill="x", padx=10, pady=10)
        
        template_label = ttk.Label(template_frame, text="Generate speech template with prepared remarks summary:")
        template_label.pack(anchor="w", pady=(5, 2))
        
        self.generate_template_button = ttk.Button(template_frame, text="Generate Template", 
                                                  command=self.generate_template)
        self.generate_template_button.pack(anchor="w", pady=(0, 5))
    
    def create_custom_speech_frame(self):
        """Create custom speech generation frame"""
        self.custom_speech_frame = ttk.LabelFrame(self.root, text="Step 4: Custom Speech Generation")
        self.custom_speech_frame.pack(fill="x", padx=10, pady=5)
        
        # Custom speech generation section
        custom_frame = ttk.Frame(self.custom_speech_frame)
        custom_frame.pack(fill="x", padx=10, pady=10)
        
        custom_label = ttk.Label(custom_frame, text="Custom Speech Generation - Enter Key Messages:")
        custom_label.pack(anchor="w", pady=(5, 2))
        
        self.key_messages_text = scrolledtext.ScrolledText(custom_frame, height=4, wrap=tk.WORD)
        self.key_messages_text.pack(fill="x", pady=(0, 5))
        
        self.generate_speech_button = ttk.Button(custom_frame, text="Generate Custom Speech", 
                                               command=self.generate_custom_speech, state="disabled")
        self.generate_speech_button.pack(anchor="w")
    
    def create_controls_frame(self):
        """Create controls frame with action buttons"""
        controls_frame = ttk.Frame(self.root)
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        # Left side - analysis info
        info_frame = ttk.Frame(controls_frame)
        info_frame.pack(side="left")
        
        self.analysis_status_label = ttk.Label(info_frame, text="Status: Ready", foreground="blue")
        self.analysis_status_label.pack(side="left")
        
        # Right side - action buttons
        right_frame = ttk.Frame(controls_frame)
        right_frame.pack(side="right")
        
        # Keep useful utility buttons
        ttk.Button(right_frame, text="Clear Logs", command=self.clear_logs).pack(side="right", padx=5)
        ttk.Button(right_frame, text="Reset", command=self.reset_app).pack(side="right", padx=5)
    
    def create_progress_frame(self):
        """Create progress bar frame"""
        progress_frame = ttk.Frame(self.root)
        progress_frame.pack(fill="x", padx=10, pady=(0, 5))
        
        self.progress_var = tk.StringVar(value="Ready")
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.pack(side="left")
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate")
        self.progress_bar.pack(side="right", fill="x", expand=True, padx=(10, 0))
    
    def create_log_frame(self):
        """Create log display frame"""
        log_frame = ttk.LabelFrame(self.root, text="Processing Log")
        log_frame.pack(fill="x", padx=10, pady=5)
        
        # Set fixed height for log frame
        log_frame.configure(height=80)
        log_frame.pack_propagate(False)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=4, state="disabled", wrap=tk.WORD)
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
    
    def create_output_frame(self):
        """Create output display frame"""
        output_frame = ttk.LabelFrame(self.root, text="Generated Output")
        output_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, state="disabled")
        self.output_text.pack(fill="both", expand=True, padx=5, pady=5)
    
    def initialize_processors(self):
        """Initialize processors and check API keys"""
        try:
            # Initialize LLM manager first
            self.llm_manager = LLMManager()
            available_providers = self.llm_manager.get_available_providers()
            
            if not available_providers:
                self.log_message("WARNING: No AI provider API keys found. Please configure your .env file.")
                self.log_message("See .env.example for required environment variables.")
                # Disable functionality that requires AI
                self.generate_template_button.config(state="disabled")
                self.generate_speech_button.config(state="disabled")
                # Initialize PDF processor without LLM manager
                self.pdf_processor = PDFProcessor()
            else:
                self.log_message(f"Available AI providers: {', '.join(available_providers)}")
                
                # Set to first available provider
                if self.llm_provider_var.get() not in available_providers:
                    self.llm_provider_var.set(available_providers[0])
                
                # Set the provider in LLM manager
                self.llm_manager.set_provider(self.llm_provider_var.get())
                
                # Initialize PDF processor with LLM manager
                self.pdf_processor = PDFProcessor(self.llm_manager)
            
            self.log_message("Speech Writer initialized successfully")
            
        except Exception as e:
            self.log_message(f"ERROR: Failed to initialize: {e}")
            messagebox.showerror("Initialization Error", f"Failed to initialize application: {e}")
    
    def browse_pdf_file(self):
        """Browse for PDF file"""
        file_path = filedialog.askopenfilename(
            title="Select PDF Transcript",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            # Clear previous PDF data when new file is selected
            self.transcript_text = None
            self.speaker_content = None
            self.current_speaker_name = None
            self.generated_output = None
            
            # Reset UI state
            self.analysis_status_label.config(text="Status: New PDF Selected", foreground="blue")
            self.generate_speech_button.config(state="disabled")
            
            self.pdf_file_var.set(file_path)
            self.log_message(f"Selected PDF: {os.path.basename(file_path)}")
            self.log_message("Previous analysis data cleared - ready for new analysis")
    
    
    def generate_template(self):
        """Generate speech template (includes analysis if needed)"""
        # Validate inputs first
        pdf_file = self.pdf_file_var.get().strip()
        speaker_name = self.speaker_name_var.get().strip()
        
        # Validate PDF file
        pdf_validation = validate_pdf_file(pdf_file)
        if not pdf_validation["is_valid"]:
            messagebox.showerror("Error", pdf_validation["error"])
            return
            
        # Validate speaker name
        name_validation = validate_speaker_name(speaker_name)
        if not name_validation["is_valid"]:
            messagebox.showerror("Error", name_validation["error"])
            return
        
        # Check if LLM manager is available
        if not hasattr(self, 'llm_manager') or not self.llm_manager.get_current_provider():
            messagebox.showerror("Error", "No AI provider available. Please configure API keys.")
            return
        
        # Run analysis and template generation in separate thread
        def run_analysis_and_template():
            try:
                self.progress_var.set("Processing PDF...")
                self.progress_bar.start()
                self.is_processing = True
                
                # Always extract text from the current PDF file to ensure fresh processing
                self.log_message(f"Extracting text from: {os.path.basename(pdf_file)}")
                pdf_data = self.pdf_processor.extract_text_from_pdf(pdf_file)
                self.transcript_text = pdf_data["full_text"]
                
                self.progress_var.set("Extracting speaker prepared remarks...")
                
                # Extract speaker content using LLM
                self.log_message(f"Extracting prepared remarks for speaker: {speaker_name}")
                self.log_message("=== SENDING PREPARED REMARKS EXTRACTION PROMPT TO LLM ===")
                speaker_data = self.pdf_processor.extract_speaker_content_via_llm(self.transcript_text, speaker_name)
                
                if not speaker_data["extraction_success"]:
                    raise Exception(speaker_data.get("error", f"Could not extract prepared remarks for speaker '{speaker_name}'"))
                
                self.speaker_content = speaker_data["content"]
                extraction_method = speaker_data.get("extraction_method", "llm")
                self.log_message(f"Extracted {len(self.speaker_content)} characters of prepared remarks using {extraction_method}")
                
                self.progress_var.set("Generating template...")
                
                # Generate template using LLM directly from prepared remarks
                self.log_message("Generating speech template...")
                self.log_message("=== SENDING TEMPLATE GENERATION PROMPT TO LLM ===")
                template = self.llm_manager.generate_template(self.speaker_content, speaker_name)
                
                # Update UI on main thread
                self.root.after(0, self._template_analysis_complete, template, speaker_name)
                
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, self._analysis_error, error_msg)
        
        # Start analysis thread
        analysis_thread = threading.Thread(target=run_analysis_and_template)
        analysis_thread.daemon = True
        analysis_thread.start()
    
    def _template_analysis_complete(self, template: str, speaker_name: str):
        """Handle successful template generation (runs on main thread)"""
        try:
            self.generated_output = template
            self.current_speaker_name = speaker_name  # Store speaker name for popup
            self.analysis_status_label.config(text=f"Status: Template Generated - {speaker_name}", foreground="green")
            
            # Enable custom speech generation
            self.generate_speech_button.config(state="normal")
            
            self.log_message("[PASS] Template generation completed successfully")
            
            # Show template window with two tabs
            self.log_message("Opening template window with prepared remarks...")
            self.show_template_with_remarks_window(template)
            
        finally:
            self.progress_bar.stop()
            self.is_processing = False
            self.progress_var.set("Ready")
    
    def generate_custom_speech(self):
        """Generate custom speech from key messages"""
        if not self.speaker_content:
            messagebox.showerror("Error", "Please generate template first to extract prepared remarks")
            return
        
        if not hasattr(self, 'llm_manager') or not self.llm_manager.get_current_provider():
            messagebox.showerror("Error", "No AI provider available")
            return
            
        key_messages = self.key_messages_text.get(1.0, tk.END).strip()
        
        # Validate key messages
        messages_validation = validate_key_messages(key_messages)
        if not messages_validation["is_valid"]:
            messagebox.showerror("Error", messages_validation["error"])
            return
        
        # Get speaker name from the UI
        speaker_name = self.speaker_name_var.get().strip()
        if not speaker_name:
            messagebox.showerror("Error", "Please enter a speaker name")
            return
        
        # Ensure speaker_content is a string, not None
        prepared_remarks = self.speaker_content if self.speaker_content is not None else ""
        
        # Run generation in separate thread
        def run_generation():
            try:
                self.progress_var.set("Generating custom speech...")
                self.progress_bar.start()
                
                self.log_message("Generating custom speech from key messages...")
                self.log_message("=== SENDING CUSTOM SPEECH GENERATION PROMPT TO LLM ===")
                
                # Generate custom speech using LLM with prepared remarks as context
                speech, prompt = self.llm_manager.generate_custom_speech(
                    prepared_remarks,  # Prepared remarks for context
                    key_messages, 
                    speaker_name
                )
                
                # Update UI on main thread
                self.root.after(0, self._speech_complete, speech, prompt)
                
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, self._generation_error, error_msg)
        
        # Start generation thread
        generation_thread = threading.Thread(target=run_generation)
        generation_thread.daemon = True
        generation_thread.start()
    
    def _speech_complete(self, speech: str, prompt: str):
        """Handle successful speech generation (runs on main thread)"""
        try:
            self.generated_output = speech
            
            self.log_message("[PASS] Custom speech generated successfully")
            
            # Show speech in popup window with prompt
            self.show_speech_window(speech, prompt)
            
        finally:
            self.progress_bar.stop()
            self.progress_var.set("Ready")
    
    def _analysis_error(self, error_msg: str):
        """Handle analysis error (runs on main thread)"""
        try:
            self.log_message(f"ERROR: Analysis failed - {error_msg}")
            messagebox.showerror("Analysis Error", f"Failed to analyze content: {error_msg}")
        finally:
            self.progress_bar.stop()
            self.is_processing = False
            self.progress_var.set("Ready")
    
    def _generation_error(self, error_msg: str):
        """Handle generation error (runs on main thread)"""
        try:
            self.log_message(f"ERROR: Generation failed - {error_msg}")
            messagebox.showerror("Generation Error", f"Failed to generate content: {error_msg}")
        finally:
            self.progress_bar.stop()
            self.progress_var.set("Ready")
    
    def display_output(self, content):
        """Display generated content in output area"""
        self.output_text.config(state="normal")
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, content)
        self.output_text.config(state="disabled")
    
    
    def export_output(self):
        """Export generated output to a file"""
        if not self.generated_output:
            messagebox.showwarning("No Output", "No generated content to export")
            return
        
        mode = self.generation_mode_var.get()
        speaker = self.speaker_name_var.get() or "Speaker"
        
        filename = f"{speaker}_{mode}_output.txt"
        
        save_path = filedialog.asksaveasfilename(
            title="Export Generated Content",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=filename
        )
        
        if save_path:
            try:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(self.generated_output)
                
                self.log_message(f"✅ Output exported: {os.path.basename(save_path)}")
                messagebox.showinfo("Export Complete", f"Content exported successfully!\n\nLocation: {save_path}")
                
            except Exception as e:
                self.log_message(f"ERROR: Export failed - {e}")
                messagebox.showerror("Export Error", f"Failed to export content: {e}")
    
    def clear_logs(self):
        """Clear the log display"""
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")
    
    def reset_app(self):
        """Reset the application to initial state"""
        # Reset variables
        self.pdf_file_var.set("")
        self.speaker_name_var.set("")
        self.generation_mode_var.set("template")
        
        # Clear text areas
        self.key_messages_text.delete(1.0, tk.END)
        self.output_text.config(state="normal")
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state="disabled")
        
        # Reset analysis data
        self.transcript_text = None
        self.speaker_content = None
        self.current_speaker_name = None
        self.generated_output = None
        
        # Reset UI states
        self.analysis_status_label.config(text="Status: Ready", foreground="blue")
        # Template button stays enabled as it handles analysis internally
        self.generate_speech_button.config(state="disabled")
        # Export button functionality removed
        
        self.progress_var.set("Ready")
        self.log_message("Application reset")
    
    def log_message(self, message):
        """Add a message to the log display"""
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.config(state="disabled")
        self.log_text.see(tk.END)
        self.root.update()
    
    def on_provider_change(self, event=None):
        """Handle AI provider change"""
        new_provider = self.llm_provider_var.get()
        
        if hasattr(self, 'llm_manager') and self.llm_manager:
            success = self.llm_manager.set_provider(new_provider)
            if success:
                self.log_message(f"AI Provider switched to: {new_provider}")
            else:
                self.log_message(f"Failed to switch to provider: {new_provider} (API key not available)")
                # Revert to previous provider
                current_provider = self.llm_manager.current_provider
                if current_provider:
                    self.llm_provider_var.set(current_provider)
        else:
            self.log_message(f"AI Provider set to: {new_provider} (will be applied after initialization)")


    
    def show_template_with_remarks_window(self, template: str):
        """Show template window with two tabs: prepared remarks and template"""
        try:
            # Validate required data before creating window
            if not self.speaker_content:
                self.log_message("ERROR: No speaker content available for template window")
                messagebox.showerror("Template Error", "No speaker content available. Please try generating the template again.")
                return
            
            speaker_name = getattr(self, 'current_speaker_name', 'Speaker')
            self.log_message(f"Creating template window for {speaker_name}. Speaker content length: {len(self.speaker_content)}")
            
            template_window = tk.Toplevel(self.root)
            template_window.title(f"Speech Analysis & Template - {speaker_name}")
            template_window.geometry("900x600")
            
            # Center the window
            template_window.update_idletasks()
            x = (template_window.winfo_screenwidth() // 2) - (450)
            y = (template_window.winfo_screenheight() // 2) - (300)
            template_window.geometry(f"900x600+{x}+{y}")
            
            # Create notebook for tabs
            notebook = ttk.Notebook(template_window)
            notebook.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Tab 1: Prepared Remarks
            remarks_frame = ttk.Frame(notebook)
            notebook.add(remarks_frame, text=f"{speaker_name}'s Prepared Remarks")
            
            remarks_text = scrolledtext.ScrolledText(remarks_frame, wrap=tk.WORD, font=("Arial", 10))
            remarks_text.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Insert prepared remarks content
            remarks_content = f"EXTRACTED PREPARED REMARKS\n"
            remarks_content += f"Speaker: {speaker_name}\n"
            remarks_content += f"Extraction Method: LLM-powered\n"
            remarks_content += f"Content Length: {len(self.speaker_content)} characters\n"
            remarks_content += "=" * 60 + "\n\n"
            remarks_content += self.speaker_content
            
            remarks_text.insert(tk.END, remarks_content)
            remarks_text.config(state="disabled")
            
            # Tab 2: Template
            template_frame = ttk.Frame(notebook)
            notebook.add(template_frame, text=f"{speaker_name}'s Speech Template")
            
            template_text = scrolledtext.ScrolledText(template_frame, wrap=tk.WORD, font=("Arial", 10))
            template_text.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Insert template content
            template_content = f"SPEECH TEMPLATE\n"
            template_content += f"Speaker: {speaker_name}\n"
            template_content += f"Generated using LLM analysis\n"
            template_content += "=" * 60 + "\n\n"
            template_content += template
            
            template_text.insert(tk.END, template_content)
            template_text.config(state="disabled")
            
            # Export buttons frame
            export_frame = ttk.Frame(template_window)
            export_frame.pack(fill="x", padx=10, pady=(0, 10))
            
            export_remarks_button = ttk.Button(export_frame, text="Export Prepared Remarks", 
                                              command=lambda: self.export_content(remarks_content, "prepared_remarks"))
            export_remarks_button.pack(side="left", padx=5)
            
            export_template_button = ttk.Button(export_frame, text="Export Template", 
                                               command=lambda: self.export_content(template_content, "template"))
            export_template_button.pack(side="left", padx=5)
            
            ttk.Button(export_frame, text="Close", command=template_window.destroy).pack(side="right")
        except Exception as e:
            self.log_message(f"ERROR: Failed to create template window: {e}")
            messagebox.showerror("Window Error", f"Failed to create template window: {str(e)}")
    
    def show_speech_window(self, speech: str, prompt: str):
        """Show custom speech in popup window with tabbed interface"""
        speech_window = tk.Toplevel(self.root)
        speaker_name = getattr(self, 'current_speaker_name', 'Speaker')
        speech_window.title(f"Custom Speech - {speaker_name}")
        speech_window.geometry("900x600")
        
        # Center the window
        speech_window.update_idletasks()
        x = (speech_window.winfo_screenwidth() // 2) - (450)
        y = (speech_window.winfo_screenheight() // 2) - (300)
        speech_window.geometry(f"900x600+{x}+{y}")
        
        # Create notebook for tabs
        notebook = ttk.Notebook(speech_window)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tab 1: Generated Speech
        speech_frame = ttk.Frame(notebook)
        notebook.add(speech_frame, text=f"Generated Speech")
        
        speech_text = scrolledtext.ScrolledText(speech_frame, wrap=tk.WORD, font=("Arial", 11))
        speech_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Insert speech content
        speech_content = f"CUSTOM SPEECH\n"
        speech_content += f"Speaker: {speaker_name}\n"
        speech_content += f"Generated using LLM with prepared remarks context\n"
        speech_content += "=" * 60 + "\n\n"
        speech_content += speech
        
        speech_text.insert(tk.END, speech_content)
        speech_text.config(state="disabled")
        
        # Tab 2: LLM Prompt
        prompt_frame = ttk.Frame(notebook)
        notebook.add(prompt_frame, text="LLM Prompt")
        
        prompt_text = scrolledtext.ScrolledText(prompt_frame, wrap=tk.WORD, font=("Arial", 10))
        prompt_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Insert prompt content
        prompt_content = f"DETAILED LLM PROMPT\n"
        prompt_content += f"Speaker: {speaker_name}\n"
        prompt_content += f"Used for custom speech generation\n"
        prompt_content += "=" * 60 + "\n\n"
        prompt_content += prompt
        
        prompt_text.insert(tk.END, prompt_content)
        prompt_text.config(state="disabled")
        
        # Export buttons frame
        export_frame = ttk.Frame(speech_window)
        export_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        export_speech_button = ttk.Button(export_frame, text="Export Speech", 
                                         command=lambda: self.export_content(speech_content, "speech"))
        export_speech_button.pack(side="left", padx=5)
        
        export_prompt_button = ttk.Button(export_frame, text="Export Prompt", 
                                         command=lambda: self.export_content(prompt_content, "prompt"))
        export_prompt_button.pack(side="left", padx=5)
        
        ttk.Button(export_frame, text="Close", command=speech_window.destroy).pack(side="right")
    
    def export_content(self, content: str, content_type: str):
        """Export content to file from popup windows"""
        speaker = self.speaker_name_var.get() or "Speaker"
        filename = f"{speaker}_{content_type}_output.txt"
        
        save_path = filedialog.asksaveasfilename(
            title=f"Export {content_type.title()}",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=filename
        )
        
        if save_path:
            try:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.log_message(f"[PASS] {content_type.title()} exported: {os.path.basename(save_path)}")
                messagebox.showinfo("Export Complete", f"{content_type.title()} exported successfully!\\n\\nLocation: {save_path}")
                
            except Exception as e:
                self.log_message(f"ERROR: Export failed - {e}")
                messagebox.showerror("Export Error", f"Failed to export {content_type}: {e}")
    
    def export_analysis_content(self, analysis: str, speaker_content: str):
        """Export both analysis and speaker content"""
        speaker = self.speaker_name_var.get() or "Speaker"
        filename = f"{speaker}_analysis_complete.txt"
        
        save_path = filedialog.asksaveasfilename(
            title="Export Complete Analysis",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=filename
        )
        
        if save_path:
            try:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(speaker_content)
                    f.write("\\n\\n" + "=" * 70 + "\\n\\n")
                    f.write(analysis)
                
                self.log_message(f"[PASS] Complete analysis exported: {os.path.basename(save_path)}")
                messagebox.showinfo("Export Complete", f"Complete analysis exported successfully!\\n\\nLocation: {save_path}")
                
            except Exception as e:
                self.log_message(f"ERROR: Export failed - {e}")
                messagebox.showerror("Export Error", f"Failed to export analysis: {e}")


def main():
    """Main function to run the application"""
    try:
        # Create and run the application
        root = tk.Tk()
        app = SpeechWriterApp(root)
        
        print("Speech Writer App started")
        root.mainloop()
        
    except Exception as e:
        print(f"Fatal error starting application: {e}")
        messagebox.showerror("Fatal Error", f"Could not start application:\n{e}")


if __name__ == "__main__":
    main()
