"""
Streaming Transcription Service using Azure Push Stream API.

This implementation uses PushAudioInputStream for real-time streaming,
matching Azure Speech Studio's approach for better accuracy.
"""

import logging
import threading
import azure.cognitiveservices.speech as speechsdk
import numpy as np
from typing import Optional, Callable, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class StreamingTranscriptionService:
    """
    Azure Speech Service with Push Stream for real-time transcription.
    
    This approach streams audio directly to Azure without file I/O,
    providing better accuracy and lower latency than file-based recognition.
    """
    
    def __init__(self, config):
        """
        Initialize streaming transcription service.
        
        Args:
            config: Configuration object with Azure credentials
        """
        self.config = config
        self.speech_config = self._create_speech_config()
        self.is_streaming = False
        self.stream = None
        self.recognizer = None
        
    def _create_speech_config(self) -> speechsdk.SpeechConfig:
        """Create Azure Speech configuration."""
        try:
            if self.config.azure_mode == "container":
                speech_config = speechsdk.SpeechConfig(
                    subscription=self.config.azure_speech_key,
                    endpoint=self.config.azure_endpoint
                )
                logger.info(f"Using container endpoint: {self.config.azure_endpoint}")
            else:
                speech_config = speechsdk.SpeechConfig(
                    subscription=self.config.azure_speech_key,
                    region=self.config.azure_region
                )
                logger.info(f"Using cloud region: {self.config.azure_region}")
            
            # Set output format to detailed
            speech_config.output_format = speechsdk.OutputFormat.Detailed
            
            # Enable dictation mode for better punctuation
            speech_config.enable_dictation()
            
            # Enable automatic punctuation
            speech_config.set_property(
                speechsdk.PropertyId.SpeechServiceResponse_RequestSentenceBoundary,
                "true"
            )
            
            # Optimize timeouts for streaming
            speech_config.set_property(
                speechsdk.PropertyId.Speech_SegmentationSilenceTimeoutMs,
                "1000"  # 1s silence for phrase boundary
            )
            
            speech_config.set_property(
                speechsdk.PropertyId.SpeechServiceConnection_EndSilenceTimeoutMs,
                "1500"  # 1.5s at end
            )
            
            # Enable word-level timestamps
            speech_config.request_word_level_timestamps()
            
            return speech_config
            
        except Exception as e:
            logger.error(f"Failed to create speech config: {e}")
            raise RuntimeError(f"Cannot create speech configuration: {e}")
    
    def start_streaming(
        self,
        language: str = "he-IL",
        callback: Optional[Callable[[Dict], None]] = None
    ) -> None:
        """
        Start streaming transcription session.
        
        Args:
            language: Language code (e.g., "he-IL" for Hebrew)
            callback: Function called when text is recognized
        
        Raises:
            RuntimeError: If streaming cannot be started
        """
        if self.is_streaming:
            logger.warning("Streaming already active")
            return
        
        try:
            # Set language
            self.speech_config.speech_recognition_language = language
            
            # Hebrew-specific optimizations
            if language == "he-IL":
                # Disable profanity filter (can misinterpret Hebrew words)
                self.speech_config.set_profanity(speechsdk.ProfanityOption.Raw)
                
                # Enable continuous language detection
                self.speech_config.set_property(
                    speechsdk.PropertyId.SpeechServiceConnection_LanguageIdMode,
                    "Continuous"
                )
                
                logger.debug("Applied Hebrew-specific optimizations")
            
            # Create push stream (16kHz, 16-bit, mono)
            stream_format = speechsdk.audio.AudioStreamFormat(
                samples_per_second=16000,
                bits_per_sample=16,
                channels=1
            )
            self.stream = speechsdk.audio.PushAudioInputStream(stream_format)
            
            # Create audio config from stream
            audio_config = speechsdk.audio.AudioConfig(stream=self.stream)
            
            # Create recognizer
            self.recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )
            
            # Storage for callback
            self.callback = callback
            
            # Connect event handlers
            def recognizing_handler(evt):
                """Intermediate results (for UI feedback)."""
                if evt.result.text:
                    logger.debug(f"Recognizing: {evt.result.text[:50]}...")
            
            def recognized_handler(evt):
                """Final transcription results."""
                if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                    text = evt.result.text.strip()
                    
                    if text and text != "...":
                        # Get confidence from detailed results
                        confidence = self._get_confidence(evt.result)
                        
                        result = {
                            "text": text,
                            "confidence": confidence,
                            "language": language,
                            "is_final": True
                        }
                        
                        logger.info(f"Stream transcript: {text[:100]}... (confidence={confidence:.2f})")
                        
                        if self.callback:
                            self.callback(result)
            
            def canceled_handler(evt):
                """Handle errors."""
                if evt.cancellation_details.reason == speechsdk.CancellationReason.Error:
                    logger.error(f"Stream error: {evt.cancellation_details.error_details}")
            
            def stopped_handler(evt):
                """Session stopped."""
                logger.debug("Stream session stopped")
                self.is_streaming = False
            
            # Connect callbacks
            self.recognizer.recognizing.connect(recognizing_handler)
            self.recognizer.recognized.connect(recognized_handler)
            self.recognizer.canceled.connect(canceled_handler)
            self.recognizer.session_stopped.connect(stopped_handler)
            
            # Start continuous recognition
            self.recognizer.start_continuous_recognition()
            self.is_streaming = True
            
            logger.info(f"Streaming transcription started (language={language})")
            
        except Exception as e:
            logger.error(f"Failed to start streaming: {e}")
            self.is_streaming = False
            raise RuntimeError(f"Cannot start streaming transcription: {e}")
    
    def push_audio(self, audio_data: np.ndarray) -> None:
        """
        Push audio data to the stream.
        
        Args:
            audio_data: Audio samples (float32, -1.0 to 1.0, mono, 16kHz)
        
        Raises:
            RuntimeError: If stream is not active
        """
        if not self.is_streaming or not self.stream:
            raise RuntimeError("Streaming not active - call start_streaming() first")
        
        try:
            # Convert float32 to int16 (Azure expects 16-bit PCM)
            audio_int16 = (audio_data * 32767).astype(np.int16)
            
            # Convert to bytes
            audio_bytes = audio_int16.tobytes()
            
            # Push to stream
            self.stream.write(audio_bytes)
            
        except Exception as e:
            logger.error(f"Failed to push audio: {e}")
            raise RuntimeError(f"Cannot push audio to stream: {e}")
    
    def stop_streaming(self) -> None:
        """Stop streaming transcription session."""
        if not self.is_streaming:
            return
        
        try:
            # Stop recognition
            if self.recognizer:
                self.recognizer.stop_continuous_recognition()
            
            # Close stream
            if self.stream:
                self.stream.close()
            
            self.is_streaming = False
            self.stream = None
            self.recognizer = None
            
            logger.info("Streaming transcription stopped")
            
        except Exception as e:
            logger.error(f"Error stopping stream: {e}")
    
    def _get_confidence(self, result) -> float:
        """
        Extract confidence score from recognition result.
        
        Args:
            result: Azure recognition result
        
        Returns:
            Confidence score (0.0-1.0)
        """
        try:
            import json
            
            # Get JSON details
            json_result = json.loads(result.json)
            
            # Extract confidence from NBest
            if "NBest" in json_result and len(json_result["NBest"]) > 0:
                return json_result["NBest"][0].get("Confidence", 0.0)
            
            return 0.5  # Default if not available
            
        except Exception as e:
            logger.debug(f"Could not extract confidence: {e}")
            return 0.5
