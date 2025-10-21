"""
Batch Processor for Speaker Diarization System.

Orchestrates all services to process audio files in batch mode,
identifying and transcribing a specific target speaker.
"""

import time
from pathlib import Path
from typing import List, Dict, Union, Optional, Callable
from datetime import datetime
import json

from src.config.config_manager import get_config
from src.utils.logger import get_logger
from src.utils.audio_utils import validate_audio_file, get_audio_duration
from src.services.diarization_service import DiarizationService
from src.services.identification_service import IdentificationService
from src.services.transcription_service import TranscriptionService
from src.services.profile_manager import ProfileManager

logger = get_logger(__name__)


class BatchProcessor:
    """
    Batch processor for speaker diarization and selective transcription.
    
    Coordinates all services to process audio files and extract transcripts
    for a specific target speaker.
    """
    
    def __init__(self, use_gpu: Optional[bool] = None):
        """
        Initialize batch processor.
        
        Args:
            use_gpu: Whether to use GPU. If None, uses config setting.
        """
        self.config = get_config()
        
        # Initialize services
        logger.info("Initializing batch processor services...")
        self.diarization = DiarizationService(use_gpu=use_gpu)
        self.identification = IdentificationService(use_gpu=use_gpu)
        self.transcription = TranscriptionService()
        self.profile_manager = ProfileManager()
        
        logger.info("Batch processor initialized")
    
    def process_file(
        self,
        audio_file: Union[str, Path],
        target_profile_id: str,
        threshold: Optional[float] = None,
        language: str = "en-US",
        num_speakers: Optional[int] = None,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> Dict:
        """
        Process a single audio file with speaker identification and transcription.
        
        Args:
            audio_file: Path to audio file
            target_profile_id: ID of target speaker profile
            threshold: Similarity threshold (uses config default if None)
            language: Language code for transcription
            num_speakers: Number of speakers (if known)
            progress_callback: Optional callback(message, progress_percent)
        
        Returns:
            Dictionary containing:
                - 'success': Boolean indicating success
                - 'audio_file': Input file path
                - 'duration': Audio duration in seconds
                - 'processing_time': Total processing time
                - 'diarization': Diarization results
                - 'identification': Identification results
                - 'transcription': Transcription results
                - 'target_profile': Target profile info
                - 'error': Error message (if failed)
        
        Raises:
            ValueError: If audio file or profile is invalid
        """
        audio_file = Path(audio_file)
        start_time = time.time()
        
        def update_progress(message: str, percent: float):
            """Helper to update progress."""
            logger.info(f"[{percent:.0f}%] {message}")
            if progress_callback:
                progress_callback(message, percent)
        
        try:
            # Validate inputs
            update_progress(f"Validating audio file: {audio_file.name}", 0)
            
            if not validate_audio_file(audio_file):
                raise ValueError(f"Invalid audio file: {audio_file}")
            
            audio_duration = get_audio_duration(audio_file)
            
            # Load target profile
            update_progress("Loading target speaker profile", 5)
            target_profile = self.profile_manager.load_profile(target_profile_id)
            target_embedding = target_profile["embedding"]
            
            # Step 1: Diarization
            update_progress("Performing speaker diarization", 10)
            segments = self.diarization.diarize(
                audio_file,
                num_speakers=num_speakers
            )
            
            if not segments:
                logger.warning("No speech segments detected")
                return self._create_result(
                    audio_file=audio_file,
                    duration=audio_duration,
                    processing_time=time.time() - start_time,
                    target_profile=target_profile,
                    success=True,
                    segments=[],
                    transcripts=[]
                )
            
            update_progress(f"Found {len(segments)} speech segments", 30)
            
            # Step 2: Identification
            update_progress("Identifying target speaker", 40)
            identified_segments = self.identification.identify_segments(
                audio_file=audio_file,
                segments=segments,
                target_embedding=target_embedding,
                threshold=threshold
            )
            
            # Count matches
            target_segments = [s for s in identified_segments if s["is_target"]]
            match_count = len(target_segments)
            match_duration = sum(s["duration"] for s in target_segments)
            
            update_progress(
                f"Identified {match_count} segments ({match_duration:.1f}s) "
                f"from target speaker",
                60
            )
            
            if match_count == 0:
                logger.warning("No segments matched target speaker")
                return self._create_result(
                    audio_file=audio_file,
                    duration=audio_duration,
                    processing_time=time.time() - start_time,
                    target_profile=target_profile,
                    success=True,
                    segments=identified_segments,
                    transcripts=[]
                )
            
            # Step 3: Transcription
            update_progress(
                f"Transcribing {match_count} target segments",
                70
            )
            
            transcripts = self.transcription.transcribe_segments(
                audio_file=audio_file,
                segments=identified_segments,
                language=language,
                target_only=True
            )
            
            update_progress("Processing complete", 100)
            
            # Calculate statistics
            processing_time = time.time() - start_time
            total_chars = sum(len(t["text"]) for t in transcripts)
            
            logger.info(
                f"Batch processing complete: {audio_file.name} "
                f"({processing_time:.1f}s, {match_count} segments, {total_chars} chars)"
            )
            
            # Create result
            result = self._create_result(
                audio_file=audio_file,
                duration=audio_duration,
                processing_time=processing_time,
                target_profile=target_profile,
                success=True,
                segments=identified_segments,
                transcripts=transcripts
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Batch processing failed for {audio_file.name}: {e}")
            processing_time = time.time() - start_time
            
            return {
                "success": False,
                "audio_file": str(audio_file),
                "processing_time": processing_time,
                "error": str(e)
            }
    
    def process_batch(
        self,
        audio_files: List[Union[str, Path]],
        target_profile_id: str,
        threshold: Optional[float] = None,
        language: str = "en-US",
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> Dict:
        """
        Process multiple audio files in batch.
        
        Args:
            audio_files: List of audio file paths
            target_profile_id: ID of target speaker profile
            threshold: Similarity threshold
            language: Language code for transcription
            progress_callback: Optional callback(message, current_file, total_files)
        
        Returns:
            Dictionary containing:
                - 'success': Boolean indicating overall success
                - 'total_files': Total number of files
                - 'successful': Number of successful files
                - 'failed': Number of failed files
                - 'results': List of individual file results
                - 'total_processing_time': Total time taken
                - 'summary': Aggregated statistics
        """
        start_time = time.time()
        
        logger.info(
            f"Starting batch processing: {len(audio_files)} files, "
            f"target profile={target_profile_id}"
        )
        
        results = []
        successful = 0
        failed = 0
        
        for i, audio_file in enumerate(audio_files, 1):
            if progress_callback:
                progress_callback(
                    f"Processing {Path(audio_file).name}",
                    i,
                    len(audio_files)
                )
            
            logger.info(f"Processing file {i}/{len(audio_files)}: {Path(audio_file).name}")
            
            try:
                result = self.process_file(
                    audio_file=audio_file,
                    target_profile_id=target_profile_id,
                    threshold=threshold,
                    language=language
                )
                
                results.append(result)
                
                if result["success"]:
                    successful += 1
                else:
                    failed += 1
                    
            except Exception as e:
                logger.error(f"Failed to process {audio_file}: {e}")
                results.append({
                    "success": False,
                    "audio_file": str(audio_file),
                    "error": str(e)
                })
                failed += 1
        
        # Calculate summary statistics
        total_time = time.time() - start_time
        summary = self._create_summary(results)
        
        logger.info(
            f"Batch processing complete: {successful} successful, {failed} failed, "
            f"{total_time:.1f}s total"
        )
        
        return {
            "success": failed == 0,
            "total_files": len(audio_files),
            "successful": successful,
            "failed": failed,
            "results": results,
            "total_processing_time": total_time,
            "summary": summary
        }
    
    def save_results(
        self,
        results: Dict,
        output_dir: Optional[Union[str, Path]] = None,
        format: str = "json"
    ) -> Path:
        """
        Save processing results to file.
        
        Args:
            results: Processing results dictionary
            output_dir: Output directory (uses config default if None)
            format: Output format ('json' or 'txt')
        
        Returns:
            Path to saved results file
        """
        if output_dir is None:
            output_dir = self.config.results_dir
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == "json":
            output_file = output_dir / f"results_{timestamp}.json"
            
            # Convert numpy arrays to lists for JSON serialization
            serializable_results = self._make_serializable(results)
            
            with open(output_file, 'w') as f:
                json.dump(serializable_results, f, indent=2)
                
        elif format == "txt":
            output_file = output_dir / f"transcript_{timestamp}.txt"
            
            with open(output_file, 'w') as f:
                self._write_text_transcript(results, f)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"Results saved to: {output_file}")
        
        return output_file
    
    def _create_result(
        self,
        audio_file: Path,
        duration: float,
        processing_time: float,
        target_profile: Dict,
        success: bool,
        segments: List[Dict],
        transcripts: List[Dict]
    ) -> Dict:
        """Create standardized result dictionary."""
        return {
            "success": success,
            "audio_file": str(audio_file),
            "filename": audio_file.name,
            "duration": duration,
            "processing_time": processing_time,
            "target_profile": {
                "id": target_profile["id"],
                "name": target_profile["name"]
            },
            "diarization": {
                "total_segments": len(segments),
                "unique_speakers": len(set(s["speaker_label"] for s in segments))
            },
            "identification": {
                "target_segments": len([s for s in segments if s.get("is_target", False)]),
                "target_duration": sum(
                    s["duration"] for s in segments if s.get("is_target", False)
                )
            },
            "transcription": {
                "total_transcripts": len(transcripts),
                "total_characters": sum(len(t["text"]) for t in transcripts),
                "transcripts": transcripts
            }
        }
    
    def _create_summary(self, results: List[Dict]) -> Dict:
        """Create summary statistics from batch results."""
        successful_results = [r for r in results if r.get("success", False)]
        
        if not successful_results:
            return {}
        
        total_duration = sum(r.get("duration", 0) for r in successful_results)
        total_processing_time = sum(r.get("processing_time", 0) for r in successful_results)
        total_segments = sum(
            r.get("diarization", {}).get("total_segments", 0)
            for r in successful_results
        )
        total_target_segments = sum(
            r.get("identification", {}).get("target_segments", 0)
            for r in successful_results
        )
        total_characters = sum(
            r.get("transcription", {}).get("total_characters", 0)
            for r in successful_results
        )
        
        return {
            "total_audio_duration": total_duration,
            "total_processing_time": total_processing_time,
            "average_processing_speed": (
                total_duration / total_processing_time
                if total_processing_time > 0 else 0
            ),
            "total_segments": total_segments,
            "total_target_segments": total_target_segments,
            "target_match_rate": (
                total_target_segments / total_segments * 100
                if total_segments > 0 else 0
            ),
            "total_characters_transcribed": total_characters
        }
    
    def _make_serializable(self, obj):
        """Convert numpy arrays and other non-serializable objects."""
        import numpy as np
        
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        elif isinstance(obj, Path):
            return str(obj)
        else:
            return obj
    
    def _write_text_transcript(self, results: Dict, file):
        """Write human-readable text transcript."""
        if "results" in results:
            # Batch results
            for result in results["results"]:
                if result.get("success"):
                    self._write_single_transcript(result, file)
        else:
            # Single file result
            self._write_single_transcript(results, file)
    
    def _write_single_transcript(self, result: Dict, file):
        """Write transcript for a single file."""
        file.write(f"{'='*80}\n")
        file.write(f"File: {result.get('filename', 'Unknown')}\n")
        file.write(f"Speaker: {result.get('target_profile', {}).get('name', 'Unknown')}\n")
        file.write(f"Duration: {result.get('duration', 0):.1f}s\n")
        file.write(f"{'='*80}\n\n")
        
        transcripts = result.get("transcription", {}).get("transcripts", [])
        
        for t in transcripts:
            timestamp = f"[{t['start']:.1f}s - {t['end']:.1f}s]"
            text = t.get("text", "")
            confidence = t.get("confidence", 0.0)
            
            file.write(f"{timestamp} {text}\n")
            file.write(f"  (confidence: {confidence:.2f})\n\n")
        
        file.write("\n")
