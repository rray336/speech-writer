"""
LLM Provider Integration Module
Handles communication with different AI providers for speech analysis and generation
"""

import os
import requests
import json
from typing import Dict, List, Optional, Any
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseLLMProvider(ABC):
    """Base class for LLM providers"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.provider_name = ""
    
    @abstractmethod
    def extract_speaker_prepared_remarks(self, full_text: str, speaker_name: str) -> str:
        """Extract speaker's prepared remarks from full document text"""
        pass
    
    @abstractmethod
    def generate_template(self, prepared_remarks: str, speaker_name: str) -> str:
        """Generate speech template based on prepared remarks"""
        pass
    
    @abstractmethod
    def generate_custom_speech(self, prepared_remarks: str, key_messages: str, speaker_name: str) -> tuple[str, str]:
        """Generate custom speech from key messages with prepared remarks as context"""
        pass

class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.provider_name = "OpenAI"
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = "gpt-4.1-mini"
    
    def _make_request(self, messages: List[Dict]) -> str:
        """Make API request to OpenAI"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code != 200:
                raise Exception(f"API request failed: {response.status_code} - {response.text}")
            
            data = response.json()
            return data["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.error(f"OpenAI API request failed: {e}")
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def extract_speaker_prepared_remarks(self, full_text: str, speaker_name: str) -> str:
        """Extract speaker's prepared remarks using OpenAI"""
        try:
            prompt = f"""
            From the following transcript, extract the prepared remarks or main presentation content by {speaker_name}.
            Look for content where {speaker_name} is:
            - Giving opening statements or prepared presentations
            - Reading from prepared scripts or notes
            - Delivering formal remarks or speeches
            - Making structured presentations (not answering questions)
            IMPORTANT: Be flexible with name matching - look for:
            - "{speaker_name}" (case-insensitive - match "john" with "John", "JOHN", etc.)
            - Variations like first name only, last name only, or titles (Mr./Ms./CEO/etc.)
            - Similar sounding names or abbreviated versions
            - Any capitalization variations of the name
            DO NOT include:
            - Q&A responses or answers to questions
            - Introductions by moderators or other people
            - Brief interjections or casual comments
            Return only the extracted prepared remarks text, without any commentary or explanation.
            If no substantial prepared content is found (only Q&A or brief comments), return "NO_PREPARED_REMARKS_FOUND".
            Transcript:
            {full_text}
            """
            messages = [
                {"role": "system", "content": "You are an expert at extracting prepared remarks from business transcripts. Extract only the formal, prepared content by the specified speaker."},
                {"role": "user", "content": prompt}
            ]
            logger.info("=== PREPARED REMARKS EXTRACTION PROMPT ===")
            logger.info(f"System: {messages[0]['content']}")
            logger.info(f"User prompt: {prompt}")
            logger.info("=== END PROMPT ===")
            response = self._make_request(messages)
            if "NO_PREPARED_REMARKS_FOUND" in response:
                raise Exception(f"No prepared remarks found for '{speaker_name}' in the document.\n\nTroubleshooting tips:\n• Verify the speaker name matches exactly as it appears in the PDF\n• Try variations like first name only or last name only\n• Check if the document contains prepared remarks (not just Q&A)\n• Ensure the speaker has substantial speaking content in the document")
            return response.strip()
        except Exception as e:
            logger.error(f"OpenAI speaker extraction failed: {e}")
            raise Exception(f"Failed to extract speaker content: {str(e)}")
    
    def generate_template(self, prepared_remarks: str, speaker_name: str) -> str:
        """Generate speech template"""
        try:
            prompt = f"""
            Assuming we are analyzing {speaker_name}'s speech.
            Review only {speaker_name}'s prepared remarks. 
            Ignore all other speakers. 
            Summarize {speaker_name}'s prepared remarks using clear sections with concise bullet points. 
            Each bullet point should be a polished, standalone sentence. 
            The goal is to create a summary that can stand on its own for presentation purposes and be detailed enough that an LLM could reconstruct the full speech if needed.
            Prepared Remarks:
            {prepared_remarks}
            """
            messages = [
                {"role": "system", "content": "You are a professional speechwriter who creates templates that capture individual speaking styles."},
                {"role": "user", "content": prompt}
            ]
            logger.info("=== TEMPLATE GENERATION PROMPT (OpenAI) ===")
            logger.info(f"System: {messages[0]['content']}")
            logger.info(f"User prompt: {prompt}")
            logger.info("=== END PROMPT ===")
            return self._make_request(messages)
        except Exception as e:
            logger.error(f"Template generation failed: {e}")
            raise Exception(f"Failed to generate template: {str(e)}")
    
    def generate_custom_speech(self, prepared_remarks: str, key_messages: str, speaker_name: str) -> tuple[str, str]:
        """Generate custom speech from key messages with prepared remarks as context, returning speech and prompt"""
        try:
            prompt = f"""
            Review only {speaker_name}'s prepared remarks in the earnings call transcripts provided. 
            Ignore all other speakers and Q&A. 
            You are also given a structured set of summary bullet points for {speaker_name}'s next speech.
            Rewrite these points into a full prepared speech in {speaker_name}'s voice and style. 
            Maintain a professional, confident, and forward-looking tone consistent with earnings call presentations. Use natural transitions between sections (Opening & Results, Consumer & Demand Trends, Segment Highlights, Strategic Initiatives, Product Quality, Closing Remarks). 
            Expand each bullet point into 1–3 sentences that could be read aloud, keeping the delivery conversational yet polished. 
            The final output should read as a cohesive script that {speaker_name} could deliver verbatim.
            Key Messages to Include:
            {key_messages}
            Original Prepared Remarks for Style Context:
            {prepared_remarks}
            """
            messages = [
                {"role": "system", "content": f"You are a professional speechwriter who specializes in mimicking the speaking style of {speaker_name}. Write speeches that sound authentic to their voice, using their prepared remarks as style context."},
                {"role": "user", "content": prompt}
            ]
            logger.info("=== CUSTOM SPEECH GENERATION PROMPT (OpenAI) ===")
            logger.info(f"System: {messages[0]['content']}")
            logger.info(f"User prompt: {prompt}")
            logger.info("=== END PROMPT ===")
            response = self._make_request(messages)
            return response, prompt
        except Exception as e:
            logger.error(f"Custom speech generation failed: {e}")
            raise Exception(f"Failed to generate custom speech: {str(e)}")

class ClaudeProvider(BaseLLMProvider):
    """Anthropic Claude provider"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.provider_name = "Claude"
        self.base_url = "https://api.anthropic.com/v1"
        self.model = "claude-3-sonnet-20240229"
    
    def _make_request(self, prompt: str) -> str:
        """Make API request to Claude"""
        try:
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            response = requests.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code != 200:
                raise Exception(f"API request failed: {response.status_code} - {response.text}")
            
            data = response.json()
            return data["content"][0]["text"]
            
        except Exception as e:
            logger.error(f"Claude API request failed: {e}")
            raise Exception(f"Claude API error: {str(e)}")
    
    def extract_speaker_prepared_remarks(self, full_text: str, speaker_name: str) -> str:
        """Extract speaker's prepared remarks using Claude"""
        try:
            prompt = f"""
            From the following transcript, extract the prepared remarks or main presentation content by {speaker_name}.
            Look for content where {speaker_name} is:
            - Giving opening statements or prepared presentations
            - Reading from prepared scripts or notes
            - Delivering formal remarks or speeches
            - Making structured presentations (not answering questions)
            IMPORTANT: Be flexible with name matching - look for:
            - "{speaker_name}" (case-insensitive - match "john" with "John", "JOHN", etc.)
            - Variations like first name only, last name only, or titles (Mr./Ms./CEO/etc.)
            - Similar sounding names or abbreviated versions
            - Any capitalization variations of the name
            DO NOT include:
            - Q&A responses or answers to questions
            - Introductions by moderators or other people
            - Brief interjections or casual comments
            Return only the extracted prepared remarks text, without any commentary or explanation.
            If no substantial prepared content is found (only Q&A or brief comments), return "NO_PREPARED_REMARKS_FOUND".
            Transcript:
            {full_text}
            """
            logger.info("=== PREPARED REMARKS EXTRACTION PROMPT (Claude) ===")
            logger.info(f"Prompt: {prompt}")
            logger.info("=== END PROMPT ===")
            response = self._make_request(prompt)
            if "NO_PREPARED_REMARKS_FOUND" in response:
                raise Exception(f"No prepared remarks found for '{speaker_name}' in the document.\n\nTroubleshooting tips:\n• Verify the speaker name matches exactly as it appears in the PDF\n• Try variations like first name only or last name only\n• Check if the document contains prepared remarks (not just Q&A)\n• Ensure the speaker has substantial speaking content in the document")
            return response.strip()
        except Exception as e:
            logger.error(f"Claude speaker extraction failed: {e}")
            raise Exception(f"Failed to extract speaker content: {str(e)}")
    
    def generate_template(self, prepared_remarks: str, speaker_name: str) -> str:
        """Generate speech template using Claude"""
        prompt = f"""
        Assuming we are analyzing {speaker_name}'s speech.
        Review only {speaker_name}'s prepared remarks. 
        Ignore all other speakers. 
        Summarize {speaker_name}'s prepared remarks using clear sections with concise bullet points. 
        Each bullet point should be a polished, standalone sentence. 
        The goal is to create a summary that can stand on its own for presentation purposes and be detailed enough that an LLM could reconstruct the full speech if needed.
        Prepared Remarks:
        {prepared_remarks}
        """
        logger.info("=== TEMPLATE GENERATION PROMPT (Claude) ===")
        logger.info(f"Prompt: {prompt}")
        logger.info("=== END PROMPT ===")
        return self._make_request(prompt)
    
    def generate_custom_speech(self, prepared_remarks: str, key_messages: str, speaker_name: str) -> tuple[str, str]:
        """Generate custom speech using Claude with prepared remarks as context, returning speech and prompt"""
        prompt = f"""Review only {speaker_name}'s prepared remarks in the earnings call transcripts provided. 
        Ignore all other speakers and Q&A. 
        You are also given a structured set of summary bullet points for {speaker_name}'s next speech.
        Rewrite these points into a full prepared speech in {speaker_name}'s voice and style. 
        Maintain a professional, confident, and forward-looking tone consistent with earnings call presentations. Use natural transitions between sections (Opening & Results, Consumer & Demand Trends, Segment Highlights, Strategic Initiatives, Product Quality, Closing Remarks). 
        Expand each bullet point into 1–3 sentences that could be read aloud, keeping the delivery conversational yet polished. 
        The final output should read as a cohesive script that {speaker_name} could deliver verbatim.
        Key Messages to Include: {key_messages}
        Original Prepared Remarks for Style Context: {prepared_remarks[:2000]}"""
        logger.info("=== CUSTOM SPEECH GENERATION PROMPT (Claude) ===")
        logger.info(f"Prompt: {prompt}")
        logger.info("=== END PROMPT ===")
        response = self._make_request(prompt)
        return response, prompt

class GeminiProvider(BaseLLMProvider):
    """Gemini LLM provider"""

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.provider_name = "Gemini"
        self.base_url = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    def _make_request(self, prompt: str) -> str:
        """Make API request to Gemini"""
        try:
            url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
            
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.7
                }
            }
            
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code != 200:
                raise Exception(f"API request failed: {response.status_code} - {response.text}")
            
            data = response.json()
            
            if "candidates" not in data or not data["candidates"]:
                raise Exception("No response candidates from Gemini API")
            
            return data["candidates"][0]["content"]["parts"][0]["text"]
            
        except Exception as e:
            logger.error(f"Gemini API request failed: {e}")
            raise Exception(f"Gemini API error: {str(e)}")

    def extract_speaker_prepared_remarks(self, full_text: str, speaker_name: str) -> str:
        """Extract speaker's prepared remarks using Gemini"""
        prompt = f"""You are an expert at extracting prepared remarks from business transcripts. Extract only the formal, prepared content by the specified speaker.

From the following transcript, extract the prepared remarks or main presentation content by {speaker_name}.
Look for content where {speaker_name} is:
- Giving opening statements or prepared presentations
- Reading from prepared scripts or notes
- Delivering formal remarks or speeches
- Making structured presentations (not answering questions)
IMPORTANT: Be flexible with name matching - look for:
- "{speaker_name}" (case-insensitive - match "john" with "John", "JOHN", etc.)
- Variations like first name only, last name only, or titles (Mr./Ms./CEO/etc.)
- Similar sounding names or abbreviated versions
- Any capitalization variations of the name
DO NOT include:
- Q&A responses or answers to questions
- Introductions by moderators or other people
- Brief interjections or casual comments
Return only the extracted prepared remarks text, without any commentary or explanation.
If no substantial prepared content is found (only Q&A or brief comments), return "NO_PREPARED_REMARKS_FOUND".
Transcript:
{full_text}"""
        
        response = self._make_request(prompt)
        if "NO_PREPARED_REMARKS_FOUND" in response:
            raise Exception(f"No prepared remarks found for '{speaker_name}' in the document.")
        return response.strip()

    def generate_template(self, prepared_remarks: str, speaker_name: str) -> str:
        """Generate speech template using Gemini"""
        prompt = f"""You are a professional speechwriter who creates templates that capture individual speaking styles.

Assuming we are analyzing {speaker_name}'s speech.
Review only {speaker_name}'s prepared remarks. 
Ignore all other speakers. 
Summarize {speaker_name}'s prepared remarks using clear sections with concise bullet points. 
Each bullet point should be a polished, standalone sentence. 
The goal is to create a summary that can stand on its own for presentation purposes and be detailed enough that an LLM could reconstruct the full speech if needed.
Prepared Remarks:
{prepared_remarks}"""
        
        return self._make_request(prompt)

    def generate_custom_speech(self, prepared_remarks: str, key_messages: str, speaker_name: str) -> tuple[str, str]:
        """Generate custom speech using Gemini with prepared remarks as context, returning speech and prompt"""
        prompt = f"""You are a professional speechwriter who specializes in mimicking the speaking style of {speaker_name}. Write speeches that sound authentic to their voice, using their prepared remarks as style context.

Review only {speaker_name}'s prepared remarks in the earnings call transcripts provided. 
Ignore all other speakers and Q&A. 
You are also given a structured set of summary bullet points for {speaker_name}'s next speech.
Rewrite these points into a full prepared speech in {speaker_name}'s voice and style. 
Maintain a professional, confident, and forward-looking tone consistent with earnings call presentations. Use natural transitions between sections (Opening & Results, Consumer & Demand Trends, Segment Highlights, Strategic Initiatives, Product Quality, Closing Remarks). 
Expand each bullet point into 1–3 sentences that could be read aloud, keeping the delivery conversational yet polished. 
The final output should read as a cohesive script that {speaker_name} could deliver verbatim.
Key Messages to Include:
{key_messages}
Original Prepared Remarks for Style Context:
{prepared_remarks}"""
        
        response = self._make_request(prompt)
        return response, prompt

class OpenrouterProvider(BaseLLMProvider):
    """Openrouter LLM provider"""

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.provider_name = "Openrouter"
        self.base_url = os.getenv("OPENROUTER_BASE_URL", "https://api.openrouter.ai/v1")
        self.model = "deepseek/deepseek-r1:free"

    def _make_request(self, messages: List[Dict]) -> str:
        """Make API request to Openrouter"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7
            }
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            if response.status_code != 200:
                raise Exception(f"API request failed: {response.status_code} - {response.text}")
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Openrouter API request failed: {e}")
            raise Exception(f"Openrouter API error: {str(e)}")

    def extract_speaker_prepared_remarks(self, full_text: str, speaker_name: str) -> str:
        """Extract speaker's prepared remarks using Openrouter"""
        prompt = f"""
        From the following transcript, extract the prepared remarks or main presentation content by {speaker_name}.
        Look for content where {speaker_name} is:
        - Giving opening statements or prepared presentations
        - Reading from prepared scripts or notes
        - Delivering formal remarks or speeches
        - Making structured presentations (not answering questions)
        IMPORTANT: Be flexible with name matching - look for:
        - "{speaker_name}" (case-insensitive - match "john" with "John", "JOHN", etc.)
        - Variations like first name only, last name only, or titles (Mr./Ms./CEO/etc.)
        - Similar sounding names or abbreviated versions
        - Any capitalization variations of the name
        DO NOT include:
        - Q&A responses or answers to questions
        - Introductions by moderators or other people
        - Brief interjections or casual comments
        Return only the extracted prepared remarks text, without any commentary or explanation.
        If no substantial prepared content is found (only Q&A or brief comments), return "NO_PREPARED_REMARKS_FOUND".
        Transcript:
        {full_text}
        """
        messages = [
            {"role": "system", "content": "You are an expert at extracting prepared remarks from business transcripts. Extract only the formal, prepared content by the specified speaker."},
            {"role": "user", "content": prompt}
        ]
        response = self._make_request(messages)
        if "NO_PREPARED_REMARKS_FOUND" in response:
            raise Exception(f"No prepared remarks found for '{speaker_name}' in the document.")
        return response.strip()

    def generate_template(self, prepared_remarks: str, speaker_name: str) -> str:
        """Generate speech template using Openrouter"""
        prompt = f"""
        Assuming we are analyzing {speaker_name}'s speech.
        Review only {speaker_name}'s prepared remarks. 
        Ignore all other speakers. 
        Summarize {speaker_name}'s prepared remarks using clear sections with concise bullet points. 
        Each bullet point should be a polished, standalone sentence. 
        The goal is to create a summary that can stand on its own for presentation purposes and be detailed enough that an LLM could reconstruct the full speech if needed.
        Prepared Remarks:
        {prepared_remarks}
        """
        messages = [
            {"role": "system", "content": "You are a professional speechwriter who creates templates that capture individual speaking styles."},
            {"role": "user", "content": prompt}
        ]
        return self._make_request(messages)

    def generate_custom_speech(self, prepared_remarks: str, key_messages: str, speaker_name: str) -> tuple[str, str]:
        """Generate custom speech using Openrouter with prepared remarks as context, returning speech and prompt"""
        prompt = f"""
        Review only {speaker_name}'s prepared remarks in the earnings call transcripts provided. 
        Ignore all other speakers and Q&A. 
        You are also given a structured set of summary bullet points for {speaker_name}'s next speech.
        Rewrite these points into a full prepared speech in {speaker_name}'s voice and style. 
        Maintain a professional, confident, and forward-looking tone consistent with earnings call presentations. Use natural transitions between sections (Opening & Results, Consumer & Demand Trends, Segment Highlights, Strategic Initiatives, Product Quality, Closing Remarks). 
        Expand each bullet point into 1–3 sentences that could be read aloud, keeping the delivery conversational yet polished. 
        The final output should read as a cohesive script that {speaker_name} could deliver verbatim.
        Key Messages to Include:
        {key_messages}
        Original Prepared Remarks for Style Context:
        {prepared_remarks}
        """
        messages = [
            {"role": "system", "content": f"You are a professional speechwriter who specializes in mimicking the speaking style of {speaker_name}. Write speeches that sound authentic to their voice, using their prepared remarks as style context."},
            {"role": "user", "content": prompt}
        ]
        response = self._make_request(messages)
        return response, prompt

class LLMManager:
    """Manager class for handling multiple LLM providers"""
    
    def __init__(self):
        self.providers = {}
        self.current_provider = None
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available providers based on API keys"""
        try:
            # OpenAI
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                self.providers["openai"] = OpenAIProvider(openai_key)
            
            # Claude
            claude_key = os.getenv("CLAUDE_API_KEY")
            if claude_key:
                self.providers["claude"] = ClaudeProvider(claude_key)
            
            # Gemini
            gemini_key = os.getenv("GEMINI_API_KEY")
            if gemini_key:
                self.providers["gemini"] = GeminiProvider(gemini_key)
            
            # Openrouter
            openrouter_key = os.getenv("OPENROUTER_API_KEY")
            if openrouter_key:
                self.providers["openrouter"] = OpenrouterProvider(openrouter_key)
            
            # Set default provider
            if self.providers:
                self.current_provider = list(self.providers.keys())[0]
                
        except Exception as e:
            logger.error(f"Error initializing LLM providers: {e}")
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return list(self.providers.keys())
    
    def set_provider(self, provider_name: str) -> bool:
        """Set the current provider"""
        if provider_name in self.providers:
            self.current_provider = provider_name
            return True
        return False
    
    def get_current_provider(self) -> Optional[BaseLLMProvider]:
        """Get the current provider instance"""
        if self.current_provider and self.current_provider in self.providers:
            return self.providers[self.current_provider]
        return None
    
    def extract_speaker_prepared_remarks(self, full_text: str, speaker_name: str) -> str:
        """Extract speaker prepared remarks using current provider"""
        provider = self.get_current_provider()
        if not provider:
            raise Exception("No LLM provider available")
        
        return provider.extract_speaker_prepared_remarks(full_text, speaker_name)
    
    def generate_template(self, prepared_remarks: str, speaker_name: str) -> str:
        """Generate template using current provider"""
        provider = self.get_current_provider()
        if not provider:
            raise Exception("No LLM provider available")
        
        return provider.generate_template(prepared_remarks, speaker_name)
    
    def generate_custom_speech(self, prepared_remarks: str, key_messages: str, speaker_name: str) -> tuple[str, str]:
        """Generate custom speech using current provider with prepared remarks as context, returning speech and prompt"""
        provider = self.get_current_provider()
        if not provider:
            raise Exception("No LLM provider available")
        
        return provider.generate_custom_speech(prepared_remarks, key_messages, speaker_name)
