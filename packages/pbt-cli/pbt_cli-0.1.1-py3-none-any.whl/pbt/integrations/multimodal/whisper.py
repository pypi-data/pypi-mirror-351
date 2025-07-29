"""
Whisper integration for PBT.
Handles speech-to-text for voice-based prompt editing and audio processing.
"""

import asyncio
import io
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import openai
import aiofiles
import tempfile
import wave
import json

from ..base import BaseIntegration


class WhisperIntegration(BaseIntegration):
    """Whisper integration for speech-to-text in prompt editing."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "whisper-1"):
        super().__init__()
        self.api_key = api_key
        self.model = model
        self.client = None
        
    async def configure(self, config: Dict[str, Any]) -> bool:
        """Configure Whisper integration."""
        try:
            self.api_key = config.get("api_key") or config.get("openai_api_key")
            self.model = config.get("model", "whisper-1")
            
            if not self.api_key:
                raise ValueError("OpenAI API key is required for Whisper")
            
            # Initialize OpenAI client
            self.client = openai.AsyncOpenAI(api_key=self.api_key)
            
            # Test connection
            return await self._test_connection()
            
        except Exception as e:
            self.logger.error(f"Failed to configure Whisper: {e}")
            return False
    
    async def _test_connection(self) -> bool:
        """Test Whisper API connection."""
        try:
            # Create a minimal test audio file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                # Create 1 second of silence
                sample_rate = 16000
                duration = 1.0
                frames = int(sample_rate * duration)
                
                with wave.open(temp_file.name, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(b'\x00' * frames * 2)
                
                # Test transcription
                with open(temp_file.name, "rb") as audio_file:
                    await self.client.audio.transcriptions.create(
                        model=self.model,
                        file=audio_file
                    )
                
                return True
                
        except Exception as e:
            self.logger.error(f"Whisper connection test failed: {e}")
            return False
    
    async def transcribe_audio(self, audio_path: Union[str, Path], 
                             language: Optional[str] = None,
                             response_format: str = "json") -> Dict[str, Any]:
        """Transcribe audio file to text."""
        try:
            audio_path = Path(audio_path)
            
            if not audio_path.exists():
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            async with aiofiles.open(audio_path, "rb") as audio_file:
                audio_data = await audio_file.read()
            
            # Create in-memory file object
            audio_buffer = io.BytesIO(audio_data)
            audio_buffer.name = audio_path.name
            
            # Transcribe audio
            transcription = await self.client.audio.transcriptions.create(
                model=self.model,
                file=audio_buffer,
                language=language,
                response_format=response_format
            )
            
            result = {
                "text": transcription.text if hasattr(transcription, 'text') else str(transcription),
                "language": language or "auto-detected",
                "duration": await self._get_audio_duration(audio_path),
                "model": self.model,
                "file_size": audio_path.stat().st_size
            }
            
            self.logger.info(f"Transcribed audio: {audio_path.name}")
            return result
            
        except Exception as e:
            self.logger.error(f"Audio transcription failed: {e}")
            raise
    
    async def transcribe_with_timestamps(self, audio_path: Union[str, Path],
                                       language: Optional[str] = None) -> Dict[str, Any]:
        """Transcribe audio with word-level timestamps."""
        try:
            audio_path = Path(audio_path)
            
            async with aiofiles.open(audio_path, "rb") as audio_file:
                audio_data = await audio_file.read()
            
            audio_buffer = io.BytesIO(audio_data)
            audio_buffer.name = audio_path.name
            
            # Request verbose JSON with timestamps
            transcription = await self.client.audio.transcriptions.create(
                model=self.model,
                file=audio_buffer,
                language=language,
                response_format="verbose_json",
                timestamp_granularities=["word"]
            )
            
            return {
                "text": transcription.text,
                "language": transcription.language,
                "duration": transcription.duration,
                "words": transcription.words if hasattr(transcription, 'words') else [],
                "segments": transcription.segments if hasattr(transcription, 'segments') else []
            }
            
        except Exception as e:
            self.logger.error(f"Timestamp transcription failed: {e}")
            raise
    
    async def translate_audio(self, audio_path: Union[str, Path],
                            target_language: str = "en") -> Dict[str, Any]:
        """Translate audio to target language."""
        try:
            audio_path = Path(audio_path)
            
            async with aiofiles.open(audio_path, "rb") as audio_file:
                audio_data = await audio_file.read()
            
            audio_buffer = io.BytesIO(audio_data)
            audio_buffer.name = audio_path.name
            
            # Use OpenAI translation endpoint
            translation = await self.client.audio.translations.create(
                model=self.model,
                file=audio_buffer
            )
            
            return {
                "original_text": translation.text,
                "translated_text": translation.text,  # Whisper translates to English by default
                "source_language": "auto-detected",
                "target_language": target_language,
                "model": self.model
            }
            
        except Exception as e:
            self.logger.error(f"Audio translation failed: {e}")
            raise
    
    async def process_voice_prompt(self, audio_path: Union[str, Path],
                                 context: Optional[str] = None) -> Dict[str, Any]:
        """Process voice input for prompt editing."""
        try:
            # Transcribe the audio
            transcription = await self.transcribe_audio(audio_path)
            
            # Extract potential prompt commands
            text = transcription["text"]
            commands = await self._extract_prompt_commands(text, context)
            
            return {
                "transcription": transcription,
                "commands": commands,
                "suggested_actions": await self._suggest_prompt_actions(text, context)
            }
            
        except Exception as e:
            self.logger.error(f"Voice prompt processing failed: {e}")
            raise
    
    async def _extract_prompt_commands(self, text: str, context: Optional[str] = None) -> List[Dict[str, Any]]:
        """Extract structured commands from transcribed text."""
        try:
            # Simple command extraction - can be enhanced with NLP
            commands = []
            
            # Look for common prompt editing commands
            command_patterns = {
                "create": ["create", "make", "generate", "new"],
                "edit": ["edit", "change", "modify", "update", "alter"],
                "delete": ["delete", "remove", "clear"],
                "test": ["test", "validate", "check"],
                "save": ["save", "store", "keep"]
            }
            
            text_lower = text.lower()
            
            for action, keywords in command_patterns.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        commands.append({
                            "action": action,
                            "keyword": keyword,
                            "confidence": 0.8,  # Simple confidence score
                            "text_segment": self._extract_relevant_segment(text, keyword)
                        })
            
            return commands
            
        except Exception as e:
            self.logger.error(f"Command extraction failed: {e}")
            return []
    
    async def _suggest_prompt_actions(self, text: str, context: Optional[str] = None) -> List[Dict[str, Any]]:
        """Suggest actions based on transcribed text."""
        try:
            suggestions = []
            
            # Analyze text for prompt creation intent
            if any(word in text.lower() for word in ["create", "make", "generate"]):
                suggestions.append({
                    "action": "create_prompt",
                    "description": "Create a new prompt based on voice input",
                    "confidence": 0.9,
                    "parameters": {
                        "content": text,
                        "type": "voice_generated"
                    }
                })
            
            # Check for editing intent
            if any(word in text.lower() for word in ["edit", "change", "modify"]):
                suggestions.append({
                    "action": "edit_prompt",
                    "description": "Edit existing prompt with voice commands",
                    "confidence": 0.8,
                    "parameters": {
                        "modifications": text,
                        "context": context
                    }
                })
            
            # Check for testing intent
            if any(word in text.lower() for word in ["test", "validate", "check"]):
                suggestions.append({
                    "action": "test_prompt",
                    "description": "Run tests based on voice instructions",
                    "confidence": 0.7,
                    "parameters": {
                        "test_criteria": text
                    }
                })
            
            return suggestions
            
        except Exception as e:
            self.logger.error(f"Action suggestion failed: {e}")
            return []
    
    def _extract_relevant_segment(self, text: str, keyword: str, context_words: int = 5) -> str:
        """Extract relevant text segment around a keyword."""
        try:
            words = text.split()
            keyword_idx = None
            
            for i, word in enumerate(words):
                if keyword.lower() in word.lower():
                    keyword_idx = i
                    break
            
            if keyword_idx is not None:
                start = max(0, keyword_idx - context_words)
                end = min(len(words), keyword_idx + context_words + 1)
                return " ".join(words[start:end])
            
            return text
            
        except Exception:
            return text
    
    async def _get_audio_duration(self, audio_path: Path) -> float:
        """Get audio file duration in seconds."""
        try:
            # Simple duration calculation for WAV files
            if audio_path.suffix.lower() == '.wav':
                with wave.open(str(audio_path), 'rb') as wav_file:
                    frames = wav_file.getnframes()
                    sample_rate = wav_file.getframerate()
                    return frames / sample_rate
            
            # For other formats, return file size approximation
            # In production, you'd use librosa or similar
            file_size = audio_path.stat().st_size
            return file_size / (16000 * 2)  # Rough estimate for 16kHz 16-bit audio
            
        except Exception:
            return 0.0
    
    async def batch_transcribe(self, audio_files: List[Union[str, Path]],
                             language: Optional[str] = None) -> List[Dict[str, Any]]:
        """Batch transcribe multiple audio files."""
        try:
            tasks = []
            
            for audio_file in audio_files:
                task = self.transcribe_audio(audio_file, language)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and handle exceptions
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append({
                        "file": str(audio_files[i]),
                        "error": str(result),
                        "success": False
                    })
                else:
                    result["file"] = str(audio_files[i])
                    result["success"] = True
                    processed_results.append(result)
            
            return processed_results
            
        except Exception as e:
            self.logger.error(f"Batch transcription failed: {e}")
            raise