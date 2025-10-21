"""
Batch Processing Tab for Streamlit UI.

Allows users to process multiple audio files and transcribe target speaker.
"""

import streamlit as st
from pathlib import Path
import tempfile
import json
from datetime import datetime

from src.processors.batch_processor import BatchProcessor
from src.services.profile_manager import ProfileManager
from src.utils.logger import get_logger

logger = get_logger(__name__)


def render_batch_tab():
    """Render the batch processing interface."""
    st.header("📁 Batch Processing")
    st.markdown("Process audio files and transcribe the target speaker")
    
    # Initialize services
    if 'batch_processor' not in st.session_state:
        st.session_state.batch_processor = BatchProcessor()
    
    if 'profile_manager' not in st.session_state:
        st.session_state.profile_manager = ProfileManager()
    
    batch_processor = st.session_state.batch_processor
    profile_manager = st.session_state.profile_manager
    
    # Check if profiles exist
    profiles = profile_manager.list_profiles()
    
    if not profiles:
        st.warning("⚠️ No speaker profiles found. Please create a profile in the Enrollment tab first.")
        return
    
    # Configuration Section
    st.subheader("⚙️ Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Profile selection
        selected_profile_id = st.selectbox(
            "Target Speaker",
            options=[p['id'] for p in profiles],
            format_func=lambda x: next(p['name'] for p in profiles if p['id'] == x),
            help="Select the speaker profile to identify and transcribe"
        )
    
    with col2:
        # Similarity threshold
        threshold = st.slider(
            "Similarity Threshold",
            min_value=0.5,
            max_value=1.0,
            value=0.75,
            step=0.05,
            help="Higher = stricter matching (fewer false positives)"
        )
    
    with col3:
        # Language selection
        language = st.selectbox(
            "Language",
            options=[
                "en-US", "en-GB", "es-ES", "fr-FR", "de-DE",
                "it-IT", "pt-BR", "ja-JP", "ko-KR", "zh-CN"
            ],
            help="Select the language for transcription"
        )
    
    st.markdown("---")
    
    # File Upload Section
    st.subheader("📤 Upload Audio Files")
    
    uploaded_files = st.file_uploader(
        "Select audio files to process",
        type=["wav", "mp3", "m4a", "flac"],
        accept_multiple_files=True,
        help="You can select multiple files for batch processing"
    )
    
    if uploaded_files:
        st.success(f"✓ {len(uploaded_files)} file(s) selected")
        
        # Show file list
        with st.expander("📋 File List", expanded=False):
            for i, file in enumerate(uploaded_files, 1):
                st.text(f"{i}. {file.name} ({file.size / 1024:.1f} KB)")
    
    # Process Button
    st.markdown("---")
    
    if st.button(
        "🚀 Start Processing",
        type="primary",
        disabled=not uploaded_files
    ):
        # Save uploaded files to temp directory
        temp_files = []
        
        with st.spinner("Preparing files..."):
            for uploaded_file in uploaded_files:
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=Path(uploaded_file.name).suffix
                ) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    temp_files.append(Path(tmp_file.name))
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def progress_callback(message, current, total):
            """Update progress bar and status."""
            progress = current / total
            progress_bar.progress(progress)
            status_text.text(f"Processing {current}/{total}: {message}")
        
        # Process files
        try:
            with st.spinner("Processing audio files..."):
                results = batch_processor.process_batch(
                    audio_files=temp_files,
                    target_profile_id=selected_profile_id,
                    threshold=threshold,
                    language=language,
                    progress_callback=progress_callback
                )
            
            # Clean up temp files
            for temp_file in temp_files:
                try:
                    temp_file.unlink()
                except:
                    pass
            
            # Store results in session state
            st.session_state.batch_results = results
            
            # Show results
            progress_bar.empty()
            status_text.empty()
            
            st.success("✅ Processing complete!")
            
            # Display summary
            st.markdown("---")
            display_batch_results(results, batch_processor)
            
        except Exception as e:
            st.error(f"❌ Processing failed: {e}")
            logger.error(f"Batch processing error: {e}")
            
            # Clean up temp files
            for temp_file in temp_files:
                try:
                    temp_file.unlink()
                except:
                    pass
    
    # Show previous results if available
    elif 'batch_results' in st.session_state and st.session_state.batch_results:
        st.markdown("---")
        st.subheader("📊 Previous Results")
        display_batch_results(st.session_state.batch_results, batch_processor)


def display_batch_results(results: dict, batch_processor: BatchProcessor):
    """Display batch processing results."""
    
    # Summary metrics
    st.subheader("📊 Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Files", results['total_files'])
    
    with col2:
        st.metric("Successful", results['successful'], delta_color="normal")
    
    with col3:
        st.metric("Failed", results['failed'], delta_color="inverse")
    
    with col4:
        st.metric(
            "Processing Time",
            f"{results['total_processing_time']:.1f}s"
        )
    
    # Additional summary stats
    if 'summary' in results and results['summary']:
        summary = results['summary']
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Match Rate",
                f"{summary.get('target_match_rate', 0):.1f}%"
            )
        
        with col2:
            st.metric(
                "Total Segments",
                f"{summary.get('total_target_segments', 0)}/{summary.get('total_segments', 0)}"
            )
        
        with col3:
            st.metric(
                "Characters",
                summary.get('total_characters_transcribed', 0)
            )
    
    st.markdown("---")
    
    # Individual file results
    st.subheader("📄 File Results")
    
    for i, result in enumerate(results['results'], 1):
        if not result.get('success'):
            with st.expander(f"❌ {result.get('filename', f'File {i}')} - Failed", expanded=False):
                st.error(f"Error: {result.get('error', 'Unknown error')}")
            continue
        
        # Successful result
        filename = result.get('filename', f'File {i}')
        target_segments = result.get('identification', {}).get('target_segments', 0)
        total_chars = result.get('transcription', {}).get('total_characters', 0)
        
        with st.expander(
            f"✓ {filename} - {target_segments} segments, {total_chars} chars",
            expanded=False
        ):
            # File info
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.text(f"Duration: {result.get('duration', 0):.1f}s")
                st.text(f"Processing Time: {result.get('processing_time', 0):.1f}s")
            
            with col_b:
                st.text(f"Total Segments: {result.get('diarization', {}).get('total_segments', 0)}")
                st.text(f"Target Segments: {target_segments}")
            
            # Transcripts
            transcripts = result.get('transcription', {}).get('transcripts', [])
            
            if transcripts:
                st.markdown("**Transcript:**")
                
                for transcript in transcripts:
                    start = transcript.get('start', 0)
                    end = transcript.get('end', 0)
                    text = transcript.get('text', '')
                    confidence = transcript.get('confidence', 0)
                    
                    st.markdown(
                        f"**[{start:.1f}s - {end:.1f}s]** {text}  \n"
                        f"*Confidence: {confidence:.2f}*"
                    )
                    st.markdown("---")
            else:
                st.info("No transcripts for this file")
    
    # Export options
    st.markdown("---")
    st.subheader("💾 Export Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Save as JSON"):
            try:
                output_file = batch_processor.save_results(results, format="json")
                st.success(f"✓ Saved to: {output_file}")
                
                # Download button
                with open(output_file, 'r') as f:
                    st.download_button(
                        "Download JSON",
                        f.read(),
                        file_name=output_file.name,
                        mime="application/json"
                    )
            except Exception as e:
                st.error(f"Failed to save: {e}")
    
    with col2:
        if st.button("📄 Save as Text"):
            try:
                output_file = batch_processor.save_results(results, format="txt")
                st.success(f"✓ Saved to: {output_file}")
                
                # Download button
                with open(output_file, 'r') as f:
                    st.download_button(
                        "Download Text",
                        f.read(),
                        file_name=output_file.name,
                        mime="text/plain"
                    )
            except Exception as e:
                st.error(f"Failed to save: {e}")
