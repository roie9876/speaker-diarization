"""
Live Monitoring Tab for Streamlit UI.

Provides real-time speaker monitoring and transcription.
"""

import streamlit as st
from datetime import datetime
import time

from src.processors.realtime_processor import RealtimeProcessor
from src.services.profile_manager import ProfileManager
from src.utils.logger import get_logger

logger = get_logger(__name__)


def render_live_tab():
    """Render the live monitoring interface."""
    st.header("🔴 Live Monitoring")
    st.markdown("Real-time speaker detection and transcription")
    
    # Initialize services
    if 'realtime_processor' not in st.session_state:
        st.session_state.realtime_processor = RealtimeProcessor()
    
    if 'profile_manager' not in st.session_state:
        st.session_state.profile_manager = ProfileManager()
    
    realtime_processor = st.session_state.realtime_processor
    profile_manager = st.session_state.profile_manager
    
    # Initialize session state
    if 'monitoring_active' not in st.session_state:
        st.session_state.monitoring_active = False
    
    if 'live_transcripts' not in st.session_state:
        st.session_state.live_transcripts = []
    
    if 'session_start_time' not in st.session_state:
        st.session_state.session_start_time = None
    
    # Check if profiles exist
    profiles = profile_manager.list_profiles()
    
    if not profiles:
        st.warning("⚠️ No speaker profiles found. Please create a profile in the Enrollment tab first.")
        return
    
    # Configuration Section
    st.subheader("⚙️ Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Audio device selection
        try:
            devices = realtime_processor.get_audio_devices()
            
            device_options = {
                device['index']: f"{device['name']} ({device['channels']} ch)"
                for device in devices
            }
            
            if device_options:
                selected_device = st.selectbox(
                    "Audio Input Device",
                    options=list(device_options.keys()),
                    format_func=lambda x: device_options[x],
                    help="Select the microphone or audio input device",
                    key="live_audio_device"
                )
            else:
                st.error("❌ No audio input devices found")
                selected_device = None
        except Exception as e:
            st.error(f"❌ Failed to enumerate audio devices: {e}")
            selected_device = None
    
    with col2:
        # Profile selection
        selected_profile_id = st.selectbox(
            "Target Speaker",
            options=[p['id'] for p in profiles],
            format_func=lambda x: next(p['name'] for p in profiles if p['id'] == x),
            help="Select the speaker profile to monitor",
            disabled=st.session_state.monitoring_active,
            key="live_target_profile"
        )
    
    with col3:
        # Similarity threshold
        threshold = st.slider(
            "Similarity Threshold",
            min_value=0.5,
            max_value=1.0,
            value=0.75,
            step=0.05,
            help="Higher = stricter matching",
            disabled=st.session_state.monitoring_active
        )
    
    # Additional settings
    col4, col5 = st.columns(2)
    
    with col4:
        language = st.selectbox(
            "Language",
            options=[
                "en-US", "en-GB", "he-IL", "es-ES", "fr-FR", "de-DE",
                "it-IT", "pt-BR", "ja-JP", "ko-KR", "zh-CN", "ar-SA"
            ],
            index=0,
            format_func=lambda x: {
                "en-US": "English (US)", "en-GB": "English (UK)",
                "he-IL": "Hebrew (Israel)", "es-ES": "Spanish (Spain)",
                "fr-FR": "French (France)", "de-DE": "German (Germany)",
                "it-IT": "Italian (Italy)", "pt-BR": "Portuguese (Brazil)",
                "ja-JP": "Japanese (Japan)", "ko-KR": "Korean (Korea)",
                "zh-CN": "Chinese (Mandarin)", "ar-SA": "Arabic (Saudi Arabia)"
            }.get(x, x),
            help="Select the language for transcription",
            disabled=st.session_state.monitoring_active,
            key="live_language"
        )
    
    st.markdown("---")
    
    # Control Section
    st.subheader("🎛️ Controls")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if not st.session_state.monitoring_active:
            if st.button(
                "▶️ Start Monitoring",
                type="primary",
                disabled=selected_device is None
            ):
                start_monitoring(
                    realtime_processor,
                    selected_device,
                    selected_profile_id,
                    threshold,
                    language
                )
        else:
            if st.button("⏹️ Stop Monitoring", type="secondary"):
                stop_monitoring(realtime_processor)
    
    with col2:
        if st.session_state.monitoring_active:
            st.success("🟢 LIVE")
        else:
            st.info("⚪ Stopped")
    
    with col3:
        if st.session_state.monitoring_active and st.session_state.session_start_time:
            elapsed = (datetime.now() - st.session_state.session_start_time).total_seconds()
            st.text(f"Session Duration: {elapsed:.0f}s")
    
    # Audio Level Meter
    if st.session_state.monitoring_active:
        st.markdown("---")
        st.subheader("📊 Audio Level")
        
        try:
            level = realtime_processor.get_audio_level()
            level_percent = min(100, level * 100)
            
            st.progress(level_percent / 100)
            st.caption(f"Level: {level_percent:.1f}%")
        except Exception as e:
            st.warning(f"Unable to read audio level: {e}")
    
    # Live Transcript Section
    st.markdown("---")
    st.subheader("📝 Live Transcript")
    
    # Transcript container
    transcript_container = st.container()
    
    with transcript_container:
        if st.session_state.live_transcripts:
            for transcript in st.session_state.live_transcripts:
                timestamp = transcript.get('timestamp', '')
                text = transcript.get('text', '')
                confidence = transcript.get('confidence', 0)
                
                st.markdown(
                    f"**[{timestamp}]** {text}  \n"
                    f"*Confidence: {confidence:.2f}*"
                )
                st.markdown("---")
        else:
            if st.session_state.monitoring_active:
                st.info("🎤 Listening... Speak to see transcripts appear here")
            else:
                st.info("Start monitoring to see live transcripts")
    
    # Session Statistics
    if st.session_state.live_transcripts:
        st.markdown("---")
        st.subheader("📈 Session Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Segments Detected",
                len(st.session_state.live_transcripts)
            )
        
        with col2:
            total_chars = sum(
                len(t.get('text', ''))
                for t in st.session_state.live_transcripts
            )
            st.metric("Characters", total_chars)
        
        with col3:
            avg_confidence = sum(
                t.get('confidence', 0)
                for t in st.session_state.live_transcripts
            ) / len(st.session_state.live_transcripts)
            st.metric("Avg Confidence", f"{avg_confidence:.2f}")
    
    # Export Session
    if st.session_state.live_transcripts and not st.session_state.monitoring_active:
        st.markdown("---")
        st.subheader("💾 Export Session")
        
        if st.button("💾 Save Session"):
            try:
                output_file = realtime_processor.save_session()
                st.success(f"✓ Session saved to: {output_file}")
                
                # Download button
                with open(output_file, 'r') as f:
                    st.download_button(
                        "Download Session",
                        f.read(),
                        file_name=output_file.name,
                        mime="text/plain"
                    )
            except Exception as e:
                st.error(f"Failed to save session: {e}")
        
        if st.button("🗑️ Clear Session"):
            st.session_state.live_transcripts = []
            st.session_state.session_start_time = None
            st.rerun()


def start_monitoring(
    processor: RealtimeProcessor,
    device_index: int,
    profile_id: str,
    threshold: float,
    language: str
):
    """Start live monitoring."""
    
    def transcript_callback(transcript: dict):
        """Callback for new transcripts."""
        # Add timestamp
        transcript['timestamp'] = datetime.now().strftime('%H:%M:%S')
        
        # Add to session state
        st.session_state.live_transcripts.append(transcript)
    
    try:
        processor.start_monitoring(
            target_profile_id=profile_id,
            audio_device_index=device_index,
            threshold=threshold,
            language=language,
            transcript_callback=transcript_callback
        )
        
        st.session_state.monitoring_active = True
        st.session_state.session_start_time = datetime.now()
        st.session_state.live_transcripts = []
        
        st.success("✓ Monitoring started")
        logger.info("Live monitoring started")
        
    except Exception as e:
        st.error(f"❌ Failed to start monitoring: {e}")
        logger.error(f"Failed to start monitoring: {e}")


def stop_monitoring(processor: RealtimeProcessor):
    """Stop live monitoring."""
    try:
        session_summary = processor.stop_monitoring()
        
        st.session_state.monitoring_active = False
        
        st.success("✓ Monitoring stopped")
        logger.info(f"Live monitoring stopped. Segments: {session_summary.get('total_segments', 0)}")
        
    except Exception as e:
        st.error(f"❌ Failed to stop monitoring: {e}")
        logger.error(f"Failed to stop monitoring: {e}")
