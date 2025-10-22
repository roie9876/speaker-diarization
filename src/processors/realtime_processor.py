"""
Real-time Processor for Speaker Diarization System.

Processes live audio streams with speaker identification and transcription.
Uses sliding window approach for continuous monitoring.
"""

import threading
import queue
import time
import numpy as np
from pathlib import Path
from typing import Optional, Callable, Dict, List
from datetime import datetime

try:
    import pyaudio
except ImportError:
    pyaudio = None
    print("Warning: pyaudio not available. Real-time processing will not work.")

from src.config.config_manager import get_config
from src.utils.logger import get_logger
from src.utils.audio_utils import save_audio, extract_segment, load_audio
from src.services.diarization_service import DiarizationService
from src.services.identification_service import IdentificationService
from src.services.transcription_service import TranscriptionService
from src.services.streaming_transcription_service import StreamingTranscriptionService
from src.services.profile_manager import ProfileManager

logger = get_logger(__name__)


class RealtimeProcessor:
    """
    Real-time processor for live speaker monitoring and transcription.
    
    Uses sliding window buffering to process audio in near real-time
    and transcribe only the target speaker.
    """
    
    def __init__(self, use_gpu: Optional[bool] = None):
        """
        Initialize real-time processor.
        
        Args:
            use_gpu: Whether to use GPU. If None, uses config setting.
        """
        self.config = get_config()
        
        # Initialize services
        logger.info("Initializing real-time processor services...")
        self.diarization = DiarizationService(use_gpu=use_gpu)
        self.identification = IdentificationService(use_gpu=use_gpu)
        self.transcription = TranscriptionService()
        self.streaming_transcription = StreamingTranscriptionService(self.config)
        self.profile_manager = ProfileManager()
        
        # Streaming mode flag (use streaming instead of file-based)
        self.use_streaming = True  # Enable by default for better accuracy
        
        # Audio stream settings
        self.sample_rate = self.config.sample_rate
        self.chunk_duration = self.config.audio_chunk_duration
        self.overlap_duration = self.config.audio_overlap_duration
        self.chunk_size = int(self.sample_rate * self.chunk_duration)
        
        # Processing state
        self.is_running = False
        self.audio_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.audio_stream = None
        self.processing_thread = None
        
        # Session data
        self.session_transcripts = []
        self.session_start_time = None
        
        # Real-time stats for UI display
        self.last_processing_stats = {
            'segments_detected': 0,
            'target_matched': False,
            'last_update': time.time()
        }
        
        # Waveform buffer for visualization (last 2 seconds)
        self.waveform_buffer_size = int(self.sample_rate * 2)  # 2 seconds
        self.waveform_buffer = np.zeros(self.waveform_buffer_size, dtype=np.float32)
        
        # Transcription buffer for continuous context
        # Accumulate target speaker audio for better transcription quality
        self.transcription_buffer = []  # List of audio segments
        self.buffer_segments = []  # Segment metadata
        self.buffer_start_time = None
        self.buffer_duration_target = 15.0  # Accumulate 15 seconds before transcribing
        self.last_transcription_time = None
        
        logger.info("Real-time processor initialized")
    
    def get_audio_devices(self) -> List[Dict]:
        """
        Get list of available audio input devices.
        
        Returns:
            List of device info dictionaries
        """
        if pyaudio is None:
            logger.error("pyaudio not available")
            return []
        
        p = pyaudio.PyAudio()
        devices = []
        
        try:
            for i in range(p.get_device_count()):
                info = p.get_device_info_by_index(i)
                
                # Only include input devices
                if info.get('maxInputChannels', 0) > 0:
                    devices.append({
                        'index': i,
                        'name': info.get('name', 'Unknown'),
                        'sample_rate': int(info.get('defaultSampleRate', 0)),
                        'channels': info.get('maxInputChannels', 0)
                    })
        finally:
            p.terminate()
        
        logger.debug(f"Found {len(devices)} audio input devices")
        
        return devices
    
    def start_monitoring(
        self,
        target_profile_id: str,
        audio_device_index: Optional[int] = None,
        threshold: Optional[float] = None,
        language: str = "en-US",
        transcript_callback: Optional[Callable[[Dict], None]] = None
    ) -> None:
        """
        Start real-time monitoring of audio input.
        
        Args:
            target_profile_id: ID of target speaker profile
            audio_device_index: Audio device index (None for default)
            threshold: Similarity threshold
            language: Language code for transcription
            transcript_callback: Callback for transcript chunks
        
        Raises:
            RuntimeError: If monitoring cannot be started
        """
        if self.is_running:
            logger.warning("Monitoring already running")
            return
        
        if pyaudio is None:
            raise RuntimeError("pyaudio not available. Cannot start monitoring.")
        
        try:
            # Load target profile
            logger.info(f"Loading target profile: {target_profile_id}")
            self.target_profile = self.profile_manager.load_profile(target_profile_id)
            self.target_embedding = self.target_profile["embedding"]
            self.threshold = threshold or self.config.similarity_threshold
            self.language = language
            self.transcript_callback = transcript_callback
            
            # Initialize session
            self.session_transcripts = []
            self.session_start_time = datetime.now()
            
            # Start streaming transcription if enabled
            if self.use_streaming:
                logger.info("Starting streaming transcription...")
                self.streaming_transcription.start_streaming(
                    language=language,
                    callback=self._handle_stream_transcript
                )
            
            # Start audio stream
            logger.info("Opening audio stream...")
            self._start_audio_stream(audio_device_index)
            
            # Start processing thread
            logger.info("Starting processing thread...")
            self.is_running = True
            self.processing_thread = threading.Thread(
                target=self._processing_loop,
                daemon=True
            )
            self.processing_thread.start()
            
            logger.info(
                f"Real-time monitoring started: "
                f"target={self.target_profile['name']}, "
                f"threshold={self.threshold:.2f}, "
                f"language={language}"
            )
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
            self.stop_monitoring()
            raise RuntimeError(f"Cannot start monitoring: {e}")
    
    def stop_monitoring(self) -> Dict:
        """
        Stop real-time monitoring and return session summary.
        
        Returns:
            Dictionary with session statistics and transcripts
        """
        logger.info("Stopping real-time monitoring...")
        
        self.is_running = False
        
        # Stop streaming transcription if enabled
        if self.use_streaming and self.streaming_transcription.is_streaming:
            logger.info("Stopping streaming transcription...")
            self.streaming_transcription.stop_streaming()
        
        # Process any remaining buffered audio before stopping (file-based fallback)
        if self.transcription_buffer:
            logger.info("Flushing remaining transcription buffer...")
            # Force transcribe whatever is in buffer
            self.buffer_duration_target = 0  # Process regardless of duration
            self._process_transcription_buffer()
        
        # Stop audio stream
        if self.audio_stream:
            try:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
            except Exception as e:
                logger.warning(f"Error closing audio stream: {e}")
            finally:
                self.audio_stream = None
        
        # Wait for processing thread
        if self.processing_thread:
            self.processing_thread.join(timeout=5.0)
            self.processing_thread = None
        
        # Create session summary
        session_duration = (
            (datetime.now() - self.session_start_time).total_seconds()
            if self.session_start_time else 0
        )
        
        summary = {
            "session_duration": session_duration,
            "total_transcripts": len(self.session_transcripts),
            "total_characters": sum(
                len(t.get("text", "")) for t in self.session_transcripts
            ),
            "transcripts": self.session_transcripts.copy(),
            "target_profile": {
                "id": self.target_profile["id"],
                "name": self.target_profile["name"]
            } if hasattr(self, 'target_profile') else None
        }
        
        logger.info(
            f"Monitoring stopped: {session_duration:.1f}s, "
            f"{len(self.session_transcripts)} transcripts"
        )
        
        return summary
    
    def _start_audio_stream(self, device_index: Optional[int]) -> None:
        """Initialize PyAudio stream."""
        p = pyaudio.PyAudio()
        
        self.audio_stream = p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=self.sample_rate,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=1024,
            stream_callback=self._audio_callback
        )
        
        self.audio_stream.start_stream()
        logger.debug(f"Audio stream opened (device={device_index})")
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback for audio stream (runs in separate thread)."""
        if status:
            logger.warning(f"Audio stream status: {status}")
        
        # Convert bytes to numpy array
        audio_data = np.frombuffer(in_data, dtype=np.float32)
        
        # DISABLED: Audio normalization was degrading quality
        # Azure Speech Service has better built-in audio processing
        # Pass raw audio for best accuracy
        
        # Add to queue for processing
        self.audio_queue.put(audio_data)
        
        # Update waveform buffer (rolling window)
        if len(audio_data) > 0:
            self.waveform_buffer = np.roll(self.waveform_buffer, -len(audio_data))
            self.waveform_buffer[-len(audio_data):] = audio_data
        
        return (in_data, pyaudio.paContinue)
    
    def _processing_loop(self) -> None:
        """Main processing loop (runs in separate thread)."""
        audio_buffer = np.array([], dtype=np.float32)
        
        logger.info("Processing loop started")
        
        while self.is_running:
            try:
                # Get audio from queue
                try:
                    audio_chunk = self.audio_queue.get(timeout=0.5)
                    audio_buffer = np.append(audio_buffer, audio_chunk)
                except queue.Empty:
                    continue
                
                # Check if we have enough audio for processing
                buffer_duration = len(audio_buffer) / self.sample_rate
                
                if buffer_duration >= self.chunk_duration:
                    # Process this chunk
                    chunk_to_process = audio_buffer[:self.chunk_size]
                    
                    # Keep overlap for next iteration
                    overlap_samples = int(self.overlap_duration * self.sample_rate)
                    audio_buffer = audio_buffer[self.chunk_size - overlap_samples:]
                    
                    # Process chunk in background
                    self._process_audio_chunk(chunk_to_process)
                
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")
                time.sleep(0.1)
        
        logger.info("Processing loop stopped")
    
    def _process_audio_chunk(self, audio_chunk: np.ndarray) -> None:
        """Process a single audio chunk."""
        try:
            # Check audio level
            rms = np.sqrt(np.mean(audio_chunk**2))
            max_amplitude = np.max(np.abs(audio_chunk))
            logger.debug(f"Audio chunk: RMS={rms:.4f}, Max={max_amplitude:.4f}, Duration={len(audio_chunk)/self.sample_rate:.1f}s")
            
            # Skip silent chunks (lowered threshold for quieter microphones)
            if rms < 0.003:  # Very quiet threshold  
                logger.debug("Chunk too quiet, skipping")
                return
            
            # Save chunk to temporary file
            temp_file = self.config.temp_dir / f"realtime_chunk_{time.time()}.wav"
            save_audio(audio_chunk, temp_file, self.sample_rate)
            
            # Step 1: Diarization
            # Force detection of multiple speakers in real-time (expect 1-3 speakers per chunk)
            # This helps detect speaker transitions when background audio is present
            segments = self.diarization.diarize(temp_file, min_speakers=1, max_speakers=3)
            
            # Update stats
            self.last_processing_stats['segments_detected'] = len(segments)
            self.last_processing_stats['target_matched'] = False
            self.last_processing_stats['last_update'] = time.time()
            
            if not segments:
                # No speech detected
                logger.debug("No speech segments detected in chunk")
                temp_file.unlink()
                return
            
            logger.info(f"Found {len(segments)} speech segment(s) in chunk")
            
            # Step 2: Identification
            identified = self.identification.identify_segments(
                audio_file=temp_file,
                segments=segments,
                target_embedding=self.target_embedding,
                threshold=self.threshold
            )
            
            # Log all detected speakers with similarity scores
            for seg in identified:
                speaker_type = "TARGET" if seg.get('is_target') else "OTHER"
                similarity = seg.get('similarity', 0.0)
                logger.info(f"  Segment [{seg['start']:.1f}s-{seg['end']:.1f}s]: {speaker_type} (similarity: {similarity:.3f})")
            
            # Filter for target speaker only
            target_segments = [s for s in identified if s.get('is_target', False)]
            
            # Update stats with match result
            self.last_processing_stats['target_matched'] = len(target_segments) > 0
            self.last_processing_stats['last_update'] = time.time()
            
            # Log target detection result
            if target_segments:
                logger.info(f"Target speaker detected in {len(target_segments)} segment(s)!")
                
                # Stream target audio directly to Azure (NEW APPROACH)
                if self.use_streaming and self.streaming_transcription.is_streaming:
                    # Stream target audio segments to Azure in real-time
                    self._stream_target_audio(temp_file, target_segments)
                else:
                    # Fallback to file-based approach
                    self._add_to_transcription_buffer(temp_file, target_segments)
                    self._process_transcription_buffer()
            else:
                logger.info("No target speaker detected in chunk")
            
            # Still transcribe other speakers immediately (without buffering)
            other_segments = [s for s in identified if not s.get('is_target', False)]
            if other_segments:
                transcripts = self.transcription.transcribe_segments(
                    audio_file=temp_file,
                    segments=other_segments,
                    language=self.language,
                    target_only=False
                )
                
                # Process other speaker transcripts
                for transcript in transcripts:
                    if transcript.get("text"):
                        transcript["timestamp"] = datetime.now().isoformat()
                        self.session_transcripts.append(transcript)
                        
                        if self.transcript_callback:
                            self.transcript_callback(transcript)
                        
                        logger.info(f"Real-time transcript [OTHER]: [{transcript['start']:.1f}s] {transcript['text'][:50]}...")
            
            # Clean up
            temp_file.unlink()
            
        except Exception as e:
            logger.error(f"Error processing audio chunk: {e}")
    
    def _add_to_transcription_buffer(self, audio_file: Path, segments: List[Dict]) -> None:
        """
        Add target speaker segments to transcription buffer for continuous context.
        
        Args:
            audio_file: Path to audio file containing segments
            segments: List of segment metadata
        """
        try:
            # Load the audio file
            from src.utils.audio_utils import load_audio
            audio, sr = load_audio(audio_file, sample_rate=self.sample_rate)
            
            # Add each target segment to buffer
            for segment in segments:
                start_sample = int(segment['start'] * sr)
                end_sample = int(segment['end'] * sr)
                segment_audio = audio[start_sample:end_sample]
                
                self.transcription_buffer.append(segment_audio)
                self.buffer_segments.append(segment)
            
            # Track buffer start time
            if self.buffer_start_time is None:
                self.buffer_start_time = time.time()
            
            # Calculate total buffered duration
            total_duration = sum(len(seg) for seg in self.transcription_buffer) / sr
            logger.debug(f"Transcription buffer: {total_duration:.1f}s accumulated")
            
        except Exception as e:
            logger.error(f"Error adding to transcription buffer: {e}")
    
    def _process_transcription_buffer(self) -> None:
        """
        Process accumulated buffer when ready (15+ seconds of target speech).
        """
        if not self.transcription_buffer:
            return
        
        try:
            # Calculate buffer duration
            total_samples = sum(len(seg) for seg in self.transcription_buffer)
            buffer_duration = total_samples / self.sample_rate
            
            # Check if buffer is ready
            time_since_start = time.time() - self.buffer_start_time if self.buffer_start_time else 0
            
            # Transcribe if: 15+ seconds accumulated OR 20+ seconds since last transcription
            should_transcribe = (
                buffer_duration >= self.buffer_duration_target or
                (self.last_transcription_time and time.time() - self.last_transcription_time > 20)
            )
            
            if should_transcribe:
                logger.info(f"Processing transcription buffer: {buffer_duration:.1f}s of target speech")
                
                # Concatenate all buffered audio
                combined_audio = np.concatenate(self.transcription_buffer)
                
                # Save to temporary file
                temp_buffer_file = self.config.temp_dir / f"buffer_{int(time.time())}.wav"
                save_audio(combined_audio, temp_buffer_file, self.sample_rate)
                
                # Create a single segment for the entire buffer
                buffer_segment = {
                    'start': 0.0,
                    'end': buffer_duration,
                    'speaker_label': 'TARGET',
                    'is_target': True,
                    'similarity': np.mean([seg.get('similarity', 0.5) for seg in self.buffer_segments])
                }
                
                # Transcribe the accumulated buffer as ONE continuous segment
                transcripts = self.transcription.transcribe_segments(
                    audio_file=temp_buffer_file,
                    segments=[buffer_segment],
                    language=self.language,
                    target_only=False
                )
                
                # Process transcripts
                for transcript in transcripts:
                    if transcript.get("text"):
                        transcript["timestamp"] = datetime.now().isoformat()
                        transcript["is_target"] = True
                        
                        # Add to session
                        self.session_transcripts.append(transcript)
                        
                        # Callback
                        if self.transcript_callback:
                            self.transcript_callback(transcript)
                        
                        logger.info(
                            f"Real-time transcript [TARGET-BUFFERED]: "
                            f"[{buffer_duration:.1f}s] {transcript['text'][:100]}... "
                            f"(confidence={transcript.get('confidence', 0):.2f})"
                        )
                
                # Clean up - wait longer to ensure all Azure callbacks are done
                try:
                    time.sleep(2.0)  # Increased to 2s for Azure to finish all processing
                    
                    # Also clean up segment temp files
                    for temp_file in self.config.temp_dir.glob("segment_*.wav"):
                        try:
                            temp_file.unlink()
                        except:
                            pass
                    
                    # Clean up buffer file
                    if temp_buffer_file.exists():
                        temp_buffer_file.unlink()
                except Exception as cleanup_error:
                    logger.warning(f"Failed to cleanup temp file: {cleanup_error}")
                
                # Clear buffer
                self._clear_transcription_buffer()
                
        except Exception as e:
            logger.error(f"Error processing transcription buffer: {e}")
    
    def _clear_transcription_buffer(self) -> None:
        """Clear the transcription buffer and reset timers."""
        self.transcription_buffer = []
        self.buffer_segments = []
        self.buffer_start_time = None
        self.last_transcription_time = time.time()
        logger.debug("Transcription buffer cleared")
    
    def _stream_target_audio(self, audio_file: Path, segments: List[Dict]) -> None:
        """
        Stream target speaker audio segments to Azure in real-time.
        
        Args:
            audio_file: Path to audio file
            segments: List of target speaker segments
        """
        try:
            # Load audio
            audio, sr = load_audio(audio_file, sample_rate=self.sample_rate)
            
            # Stream each target segment
            for segment in segments:
                start_sample = int(segment['start'] * sr)
                end_sample = int(segment['end'] * sr)
                segment_audio = audio[start_sample:end_sample]
                
                # Push audio to stream
                self.streaming_transcription.push_audio(segment_audio)
                
                logger.debug(f"Streamed {len(segment_audio)} samples to Azure")
                
        except Exception as e:
            logger.error(f"Error streaming target audio: {e}")
    
    def _handle_stream_transcript(self, result: Dict) -> None:
        """
        Handle transcript from streaming service.
        
        Args:
            result: Transcript result from streaming service
        """
        try:
            if result.get("text"):
                # Add metadata
                result["timestamp"] = datetime.now().isoformat()
                result["is_target"] = True
                result["speaker_label"] = "TARGET"
                
                # Add to session
                self.session_transcripts.append(result)
                
                # Callback to UI
                if self.transcript_callback:
                    self.transcript_callback(result)
                
                logger.info(
                    f"Real-time transcript [STREAM]: "
                    f"{result['text'][:100]}... "
                    f"(confidence={result.get('confidence', 0):.2f})"
                )
                
        except Exception as e:
            logger.error(f"Error handling stream transcript: {e}")
    
    def get_audio_level(self) -> float:
        """
        Get current audio input level (0.0-1.0).
        
        Returns:
            Audio level as float
        """
        if not self.is_running or self.audio_queue.empty():
            return 0.0
        
        try:
            # Peek at recent audio without removing from queue
            recent_audio = []
            temp_items = []
            
            # Get up to 10 recent chunks
            for _ in range(min(10, self.audio_queue.qsize())):
                try:
                    chunk = self.audio_queue.get_nowait()
                    temp_items.append(chunk)
                    recent_audio.append(chunk)
                except queue.Empty:
                    break
            
            # Put them back
            for item in temp_items:
                self.audio_queue.put(item)
            
            if recent_audio:
                combined = np.concatenate(recent_audio)
                level = np.abs(combined).mean()
                return float(min(1.0, level * 10))  # Scale up for visibility
            
        except Exception as e:
            logger.debug(f"Error getting audio level: {e}")
        
        return 0.0
    
    def save_session(
        self,
        output_dir: Optional[Path] = None
    ) -> Path:
        """
        Save session transcripts to file.
        
        Args:
            output_dir: Output directory (uses config default if None)
        
        Returns:
            Path to saved file
        """
        if output_dir is None:
            output_dir = self.config.results_dir
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"realtime_session_{timestamp}.txt"
        
        # Write transcripts
        with open(output_file, 'w') as f:
            f.write(f"Real-time Session Transcript\n")
            f.write(f"{'='*80}\n")
            f.write(f"Speaker: {self.target_profile['name']}\n")
            f.write(f"Started: {self.session_start_time.isoformat()}\n")
            f.write(f"{'='*80}\n\n")
            
            for transcript in self.session_transcripts:
                timestamp_str = transcript.get("timestamp", "Unknown")
                text = transcript.get("text", "")
                confidence = transcript.get("confidence", 0.0)
                
                f.write(f"[{timestamp_str}]\n")
                f.write(f"{text}\n")
                f.write(f"(confidence: {confidence:.2f})\n\n")
        
        logger.info(f"Session saved to: {output_file}")
        
        return output_file
    
    def get_waveform_data(self, num_samples: int = 100) -> np.ndarray:
        """
        Get downsampled waveform data for visualization.
        
        Args:
            num_samples: Number of samples to return (for plotting)
        
        Returns:
            Downsampled waveform array
        """
        if not self.is_running:
            return np.zeros(num_samples, dtype=np.float32)
        
        try:
            # Downsample the waveform buffer for visualization
            buffer_len = len(self.waveform_buffer)
            if buffer_len == 0:
                return np.zeros(num_samples, dtype=np.float32)
            
            # Calculate downsample factor
            downsample_factor = max(1, buffer_len // num_samples)
            
            # Downsample by taking max of each window (preserves peaks)
            downsampled = []
            for i in range(0, buffer_len, downsample_factor):
                window = self.waveform_buffer[i:i+downsample_factor]
                if len(window) > 0:
                    # Take max absolute value to preserve peaks
                    downsampled.append(np.max(np.abs(window)) * np.sign(np.mean(window)))
            
            result = np.array(downsampled[:num_samples], dtype=np.float32)
            
            # Pad if needed
            if len(result) < num_samples:
                result = np.pad(result, (0, num_samples - len(result)), mode='constant')
            
            return result
            
        except Exception as e:
            logger.debug(f"Error getting waveform data: {e}")
            return np.zeros(num_samples, dtype=np.float32)
