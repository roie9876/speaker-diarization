"""
Transcription Service using Azure Cognitive Services Speech SDK.

Provides speech-to-text transcription functionality with support for
both cloud and container deployments.
"""

import azure.cognitiveservices.speech as speechsdk
import numpy as np
from pathlib import Path
from typing import List, Dict, Union, Optional
from src.config.config_manager import get_config
from src.utils.logger import get_logger
from src.utils.audio_utils import (
    validate_audio_file,
    load_audio,
    extract_segment,
    save_audio
)

logger = get_logger(__name__)


class TranscriptionService:
    """
    Service for speech-to-text transcription using Azure Speech Service.
    
    Supports both cloud and container deployments.
    """
    
    def __init__(self):
        """Initialize transcription service."""
        self.config = get_config()
        self.speech_config = self._create_speech_config()
        logger.info(
            f"Transcription service initialized "
            f"(mode={self.config.azure_mode}, region={self.config.azure_region})"
        )
    
    def _create_speech_config(self) -> speechsdk.SpeechConfig:
        """
        Create Azure Speech SDK configuration.
        
        Returns:
            Configured SpeechConfig instance
        
        Raises:
            RuntimeError: If configuration fails
        """
        try:
            if self.config.azure_mode == "container":
                # Container mode
                if not self.config.azure_endpoint:
                    raise ValueError(
                        "AZURE_ENDPOINT must be set for container mode"
                    )
                
                speech_config = speechsdk.SpeechConfig(
                    subscription=self.config.azure_speech_key,
                    endpoint=self.config.azure_endpoint
                )
                logger.info(f"Using container endpoint: {self.config.azure_endpoint}")
                
            else:
                # Cloud mode
                speech_config = speechsdk.SpeechConfig(
                    subscription=self.config.azure_speech_key,
                    region=self.config.azure_region
                )
                logger.info(f"Using cloud region: {self.config.azure_region}")
            
            # Set output format to detailed
            speech_config.output_format = speechsdk.OutputFormat.Detailed
            
            # Enable profanity filter (can be disabled if needed)
            speech_config.set_profanity(speechsdk.ProfanityOption.Masked)
            
            # Enable punctuation for better readability
            speech_config.enable_dictation()
            
            # Optimize for accuracy in continuous speech recognition
            # Enable sentence boundary detection
            speech_config.set_property(
                speechsdk.PropertyId.SpeechServiceResponse_RequestSentenceBoundary,
                "true"
            )
            
            # Enable automatic punctuation (improves accuracy)
            speech_config.set_property(
                speechsdk.PropertyId.SpeechServiceResponse_ProfanityOption,
                "masked"
            )
            
            # Set segmentation silence timeout (in milliseconds)
            # For Hebrew speech, need longer timeout to avoid mid-sentence cuts
            # Increased from 800ms to 1500ms for complete phrases
            speech_config.set_property(
                speechsdk.PropertyId.Speech_SegmentationSilenceTimeoutMs,
                "1500"  # 1.5s of silence before considering phrase ended
            )
            
            # Enable word-level timing (useful for debugging)
            speech_config.request_word_level_timestamps()
            
            # Set initial silence timeout (how long to wait before starting recognition)
            speech_config.set_property(
                speechsdk.PropertyId.SpeechServiceConnection_InitialSilenceTimeoutMs,
                "5000"  # 5 seconds - give time for speech to start
            )
            
            # Set end silence timeout (for better phrase detection)
            # Increased to 2 seconds to capture complete sentences
            speech_config.set_property(
                speechsdk.PropertyId.SpeechServiceConnection_EndSilenceTimeoutMs,
                "2000"  # 2 seconds of silence at end
            )
            
            return speech_config
            
        except Exception as e:
            logger.error(f"Failed to create speech config: {e}")
            raise RuntimeError(f"Cannot create speech configuration: {e}")
    
    def transcribe_file(
        self,
        audio_file: Union[str, Path],
        language: str = "en-US",
        use_continuous: bool = False
    ) -> Dict:
        """
        Transcribe an entire audio file.
        
        Args:
            audio_file: Path to audio file
            language: Language code (e.g., 'en-US', 'es-ES')
            use_continuous: If True, use continuous recognition for longer speech
        
        Returns:
            Dictionary containing:
                - 'text': Transcribed text
                - 'confidence': Confidence score (0.0-1.0)
                - 'duration': Audio duration in seconds
                - 'language': Language code used
        
        Raises:
            ValueError: If audio file is invalid
            RuntimeError: If transcription fails
        """
        audio_file = Path(audio_file)
        
        # Validate audio
        if not validate_audio_file(audio_file):
            raise ValueError(f"Invalid audio file: {audio_file}")
        
        logger.info(f"Transcribing file: {audio_file.name} (language={language}, continuous={use_continuous})")
        
        try:
            # Set language
            self.speech_config.speech_recognition_language = language
            
            # Hebrew-specific optimizations for better accuracy
            if language == "he-IL":
                # Disable profanity filter for Hebrew (can misinterpret words)
                self.speech_config.set_profanity(speechsdk.ProfanityOption.Raw)
                
                # Enable diacritics for Hebrew (niqqud) - improves accuracy
                self.speech_config.set_property(
                    speechsdk.PropertyId.SpeechServiceResponse_RequestWordLevelTimestamps,
                    "true"
                )
                
                # Use detailed output format for better confidence scores
                self.speech_config.output_format = speechsdk.OutputFormat.Detailed
                
                # Enable language detection for better Hebrew recognition
                self.speech_config.set_property(
                    speechsdk.PropertyId.SpeechServiceConnection_LanguageIdMode,
                    "Continuous"
                )
                
                logger.debug("Applied Hebrew-specific optimizations (disabled profanity filter, enabled diacritics)")
            
            # Create audio config
            audio_config = speechsdk.audio.AudioConfig(filename=str(audio_file))
            
            # Create speech recognizer
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=self.speech_config,
                audio_config=audio_config
            )
            
            # Use continuous recognition for longer segments
            if use_continuous:
                return self._transcribe_continuous(recognizer)
            
            # Otherwise use single-shot recognition with extended timeout
            # Perform recognition
            result = recognizer.recognize_once()
            
            # Process result
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                # Get confidence from detailed results
                confidence = self._get_confidence(result)
                
                logger.info(
                    f"Transcription successful: {len(result.text)} chars, "
                    f"confidence={confidence:.2f}"
                )
                
                # result.duration is in 100-nanosecond units (ticks)
                # Convert to seconds: ticks / 10,000,000
                duration_seconds = result.duration / 10_000_000 if isinstance(result.duration, int) else 0.0
                
                return {
                    "text": result.text,
                    "confidence": confidence,
                    "duration": duration_seconds,
                    "language": language
                }
                
            elif result.reason == speechsdk.ResultReason.NoMatch:
                logger.warning("No speech recognized")
                return {
                    "text": "",
                    "confidence": 0.0,
                    "duration": 0.0,
                    "language": language
                }
                
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation = result.cancellation_details
                logger.error(f"Transcription canceled: {cancellation.reason}")
                if cancellation.reason == speechsdk.CancellationReason.Error:
                    raise RuntimeError(
                        f"Transcription error: {cancellation.error_details}"
                    )
                return {
                    "text": "",
                    "confidence": 0.0,
                    "duration": 0.0,
                    "language": language
                }
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise RuntimeError(f"Cannot transcribe audio: {e}")
    
    def _transcribe_continuous(self, recognizer: speechsdk.SpeechRecognizer) -> Dict:
        """
        Use continuous recognition to transcribe entire audio stream.
        Better for longer segments with continuous speech.
        Uses fast transcription mode optimized for real-time scenarios.
        
        Args:
            recognizer: Configured speech recognizer
        
        Returns:
            Dictionary with transcription results
        """
        import threading
        
        # Storage for results
        results = {
            "texts": [],
            "confidences": [],
            "done": threading.Event(),
            "error": None,
            "stopped": False  # Flag to prevent processing after stop
        }
        
        def recognizing_callback(evt):
            """Called during recognition (intermediate results)."""
            # Only log first few to avoid spam
            if not results["stopped"] and evt.result.text and len(results["texts"]) < 2:
                logger.debug(f"Recognizing: {evt.result.text[:30]}...")
        
        def recognized_callback(evt):
            """Called when speech is recognized (final results)."""
            # Stop processing if already stopped
            if results["stopped"]:
                return
                
            if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                text = evt.result.text.strip()
                confidence = self._get_confidence(evt.result)
                
                # Filter out low-confidence and invalid results
                # Skip if: empty, only dots, or confidence too low
                if text and text != "..." and confidence > 0.3:
                    # Avoid duplicates - check if this text was already added
                    if not results["texts"] or text != results["texts"][-1]:
                        results["texts"].append(text)
                        results["confidences"].append(confidence)
                        logger.debug(f"Recognized: {text[:50]}... (confidence={confidence:.2f})")
                else:
                    logger.debug(f"Skipping low-quality result: '{text}' (confidence={confidence:.2f})")
        
        def canceled_callback(evt):
            """Called when recognition is canceled."""
            if evt.cancellation_details.reason == speechsdk.CancellationReason.Error:
                error_msg = f"Recognition error: {evt.cancellation_details.error_details}"
                logger.error(error_msg)
                results["error"] = error_msg
            results["done"].set()
        
        def stopped_callback(evt):
            """Called when recognition stops."""
            results["stopped"] = True  # Set flag to stop processing
            logger.debug("Recognition session stopped")
            results["done"].set()
        
        # Connect callbacks
        recognizer.recognizing.connect(recognizing_callback)  # Intermediate results
        recognizer.recognized.connect(recognized_callback)     # Final results
        recognizer.canceled.connect(canceled_callback)
        recognizer.session_stopped.connect(stopped_callback)
        
        # Start continuous recognition
        logger.debug("Starting continuous recognition with fast transcription...")
        recognizer.start_continuous_recognition()
        
        # Wait for completion (with timeout - 15 seconds for 8s buffer)
        if not results["done"].wait(timeout=20):
            logger.warning("Continuous recognition timed out")
            results["stopped"] = True  # Mark as stopped
            recognizer.stop_continuous_recognition()
        
        # Stop recognition
        results["stopped"] = True  # Mark as stopped before calling stop
        recognizer.stop_continuous_recognition()
        
        # Check for errors
        if results["error"]:
            logger.error(f"Transcription error: {results['error']}")
            return {
                "text": "",
                "confidence": 0.0,
                "duration": 0.0,
                "language": "unknown",
                "error": results["error"]
            }
        
        # Combine results
        full_text = " ".join(results["texts"]).strip()
        avg_confidence = np.mean(results["confidences"]) if results["confidences"] else 0.0
        
        logger.debug(f"Fast transcription complete: {len(full_text)} chars, {len(results['texts'])} phrases")
        
        return {
            "text": full_text,
            "confidence": avg_confidence,
            "duration": 0.0,  # Not available in continuous mode
            "language": recognizer.properties.get_property(
                speechsdk.PropertyId.SpeechServiceConnection_RecoLanguage
            ) or "unknown"
        }
    
    def transcribe_segment(
        self,
        audio_file: Union[str, Path],
        start: float,
        end: float,
        language: str = "en-US",
        use_continuous: bool = False
    ) -> Dict:
        """
        Transcribe a segment of an audio file.
        
        Args:
            audio_file: Path to audio file
            start: Start time in seconds
            end: End time in seconds
            language: Language code
            use_continuous: Use continuous recognition (for segments >5s, otherwise single-shot)
        
        Returns:
            Dictionary with transcription results
        """
        audio_file = Path(audio_file)
        segment_duration = end - start
        
        logger.debug(f"Transcribing segment [{start:.2f}s - {end:.2f}s] (duration={segment_duration:.2f}s)")
        
        try:
            # Load audio and extract segment
            audio, sr = load_audio(audio_file, sample_rate=self.config.sample_rate)
            segment_audio = extract_segment(audio, sr, start, end)
            
            # DISABLED: Audio preprocessing was degrading quality
            # Azure Speech Service handles normalization better internally
            # Just pass the raw audio without modifications
            
            # Save segment to temporary file
            temp_file = self.config.temp_dir / f"segment_{start:.2f}_{end:.2f}.wav"
            save_audio(segment_audio, temp_file, sr)
            
            # Choose recognition mode based on segment duration
            # recognize_once: Good for <10s (better quality, but has max duration limit)
            # continuous: Required for >10s (handles any duration)
            use_continuous_mode = segment_duration > 10.0
            
            # Transcribe segment
            result = self.transcribe_file(temp_file, language=language, use_continuous=use_continuous_mode)
            
            # Add timing information
            result["start"] = start
            result["end"] = end
            
            # DON'T delete temp file immediately - Azure might still be processing
            # It will be cleaned up by the caller or on next run
            # This prevents "file not found" race condition errors
            
            return result
            
        except Exception as e:
            logger.error(f"Segment transcription failed: {e}")
            raise RuntimeError(f"Cannot transcribe segment: {e}")
    
    def transcribe_segments(
        self,
        audio_file: Union[str, Path],
        segments: List[Dict],
        language: str = "en-US",
        target_only: bool = True
    ) -> List[Dict]:
        """
        Transcribe multiple segments from an audio file.
        
        Args:
            audio_file: Path to audio file
            segments: List of segments (must have 'start', 'end', and optionally 'is_target')
            language: Language code
            target_only: If True, only transcribe segments where is_target=True
        
        Returns:
            List of transcription results with timing information
        """
        audio_file = Path(audio_file)
        
        # Filter segments if needed
        if target_only:
            segments_to_transcribe = [
                seg for seg in segments
                if seg.get("is_target", False)
            ]
            logger.info(
                f"Transcribing {len(segments_to_transcribe)}/{len(segments)} "
                f"target segments"
            )
        else:
            segments_to_transcribe = segments
            logger.info(f"Transcribing all {len(segments)} segments")
        
        results = []
        
        for i, segment in enumerate(segments_to_transcribe, 1):
            try:
                result = self.transcribe_segment(
                    audio_file,
                    start=segment["start"],
                    end=segment["end"],
                    language=language
                )
                
                # Add segment metadata
                result["speaker_label"] = segment.get("speaker_label", "UNKNOWN")
                result["similarity"] = segment.get("similarity", 0.0)
                result["is_target"] = segment.get("is_target", False)  # CRITICAL: Preserve is_target flag
                
                results.append(result)
                
                logger.debug(
                    f"Segment {i}/{len(segments_to_transcribe)}: "
                    f"{len(result['text'])} chars, confidence={result['confidence']:.2f}"
                )
                
            except Exception as e:
                logger.warning(f"Failed to transcribe segment {i}: {e}")
                # Add empty result
                results.append({
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": "",
                    "confidence": 0.0,
                    "speaker_label": segment.get("speaker_label", "UNKNOWN"),
                    "similarity": segment.get("similarity", 0.0),
                    "is_target": segment.get("is_target", False),  # Preserve is_target flag
                    "language": language
                })
        
        # Log summary
        total_chars = sum(len(r["text"]) for r in results)
        avg_confidence = np.mean([r["confidence"] for r in results if r["confidence"] > 0])
        
        logger.info(
            f"Transcription complete: {len(results)} segments, "
            f"{total_chars} chars, avg_confidence={avg_confidence:.2f}"
        )
        
        return results
    
    def _get_confidence(self, result: speechsdk.SpeechRecognitionResult) -> float:
        """
        Extract confidence score from recognition result.
        
        Args:
            result: Speech recognition result
        
        Returns:
            Confidence score (0.0-1.0)
        """
        try:
            import json
            details = json.loads(result.json)
            
            # Get best result confidence
            if "NBest" in details and len(details["NBest"]) > 0:
                return details["NBest"][0].get("Confidence", 0.0)
            
        except Exception as e:
            logger.debug(f"Could not extract confidence: {e}")
        
        # Default confidence
        return 0.5
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported language codes.
        
        Returns:
            List of language codes
        """
        # Common languages - full list available in Azure docs
        return [
            "en-US", "en-GB", "es-ES", "es-MX", "fr-FR", "de-DE",
            "it-IT", "pt-BR", "pt-PT", "ja-JP", "ko-KR", "zh-CN",
            "zh-TW", "ar-SA", "hi-IN", "ru-RU", "nl-NL", "pl-PL"
        ]
