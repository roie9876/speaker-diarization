"""
Live Monitoring Tab for Streamlit UI.

Provides real-time speaker monitoring and transcription.
"""

import streamlit as st
from datetime import datetime
import time
import numpy as np
import plotly.graph_objects as go

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
    
    if 'transcript_queue' not in st.session_state:
        import queue
        st.session_state.transcript_queue = queue.Queue()
    
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
            
            # Find default device
            default_device_index = None
            try:
                import pyaudio
                p = pyaudio.PyAudio()
                default_device_index = p.get_default_input_device_info()['index']
                p.terminate()
            except:
                pass
            
            device_options = {
                device['index']: f"{device['name']}{' 🎤 DEFAULT' if device['index'] == default_device_index else ''} ({device['channels']} ch)"
                for device in devices
            }
            
            if device_options:
                # Default to the system default device
                default_selection = default_device_index if default_device_index in device_options else list(device_options.keys())[0]
                
                selected_device = st.selectbox(
                    "Audio Input Device",
                    options=list(device_options.keys()),
                    format_func=lambda x: device_options[x],
                    index=list(device_options.keys()).index(default_selection) if default_selection in device_options else 0,
                    help="⚠️ Use the DEFAULT device - same as used for enrollment!",
                    key="live_audio_device"
                )
                
                # Warning if not using default
                if selected_device != default_device_index:
                    st.warning("⚠️ You're using a different device than the default. Use the DEFAULT device (marked with 🎤) for best results!")
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
            value=0.50,
            step=0.05,
            help="Higher = stricter matching (0.50 recommended for this system)",
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
    
    # CRITICAL: Pull transcripts from queue at the start of each render cycle
    if st.session_state.monitoring_active:
        logger.debug(f"Checking for transcripts... has queue attr: {hasattr(realtime_processor, 'ui_transcript_queue')}")
        
        if hasattr(realtime_processor, 'ui_transcript_queue'):
            import queue
            try:
                # Get all available transcripts from queue (non-blocking)
                pulled_count = 0
                while True:
                    try:
                        transcript = realtime_processor.ui_transcript_queue.get_nowait()
                        st.session_state.live_transcripts.append(transcript)
                        pulled_count += 1
                        logger.debug(f"Pulled transcript from queue: {transcript.get('text', '')[:30]}...")
                    except queue.Empty:
                        break
                
                if pulled_count > 0:
                    logger.info(f"Pulled {pulled_count} transcript(s) from queue, total now: {len(st.session_state.live_transcripts)}")
                    
            except Exception as e:
                logger.error(f"Error pulling from transcript queue: {e}")
        else:
            logger.warning(f"⚠️ No ui_transcript_queue found on processor (id: {id(realtime_processor)})")
    
    # Audio Level Meter & Voice Detection
    if st.session_state.monitoring_active:
        st.markdown("---")
        
        # Waveform Visualization
        st.subheader("🎙️ Live Audio Waveform")
        try:
            # Get waveform data from processor
            waveform = realtime_processor.get_waveform_data(num_samples=200)
            
            # Create time axis (in seconds, last 2 seconds)
            time_axis = np.linspace(-2, 0, len(waveform))
            
            # Create plotly figure with better styling
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=time_axis,
                y=waveform,
                mode='lines',
                line=dict(color='#1f77b4', width=1),
                fill='tozeroy',
                fillcolor='rgba(31, 119, 180, 0.3)',
                name='Audio',
                hovertemplate='Time: %{x:.2f}s<br>Amplitude: %{y:.3f}<extra></extra>'
            ))
            
            fig.update_layout(
                xaxis_title="Time (seconds)",
                yaxis_title="Amplitude",
                height=200,
                margin=dict(l=20, r=20, t=20, b=40),
                plot_bgcolor='rgba(240, 242, 246, 0.5)',
                paper_bgcolor='white',
                xaxis=dict(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='rgba(128, 128, 128, 0.2)',
                    zeroline=True,
                    zerolinewidth=2,
                    zerolinecolor='rgba(128, 128, 128, 0.3)'
                ),
                yaxis=dict(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='rgba(128, 128, 128, 0.2)',
                    zeroline=True,
                    zerolinewidth=2,
                    zerolinecolor='rgba(128, 128, 128, 0.3)',
                    range=[-1, 1]
                ),
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True, key=f"waveform_{time.time()}")
            
        except Exception as e:
            st.warning(f"Unable to display waveform: {e}")
        
        # Audio Level & Speech Detection
        col_a, col_b = st.columns([1, 1])
        
        with col_a:
            st.subheader("📊 Audio Level")
            try:
                level = realtime_processor.get_audio_level()
                level_percent = min(100, level * 100)
                
                st.progress(level_percent / 100)
                
                # Voice activity indicator
                if level_percent > 1.0:  # Above 1% means audio detected
                    st.success(f"🎤 Detecting: {level_percent:.1f}%")
                else:
                    st.info(f"🔇 Silent: {level_percent:.1f}%")
            except Exception as e:
                st.warning(f"Unable to read audio level: {e}")
        
        with col_b:
            st.subheader("🗣️ Speech Detection")
            # Get processing stats from realtime processor
            if hasattr(realtime_processor, 'last_processing_stats'):
                stats = realtime_processor.last_processing_stats
                segments_detected = stats.get('segments_detected', 0)
                target_matched = stats.get('target_matched', False)
                
                if segments_detected > 0:
                    st.success(f"✓ Voice detected ({segments_detected} segment(s))")
                    if target_matched:
                        st.success("🎯 **Target speaker detected!**")
                    else:
                        st.warning("❌ Not target speaker")
                else:
                    st.info("👂 Listening...")
            else:
                st.info("👂 Waiting for audio...")
    
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
    
    # Auto-refresh: Trigger rerun at the VERY END after all UI elements are rendered
    # This ensures transcripts, waveforms, and stats are displayed before the next cycle
    if st.session_state.monitoring_active:
        time.sleep(0.5)  # Brief pause between refresh cycles
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
        """Callback for new transcripts from background thread."""
        # Add timestamp
        transcript['timestamp'] = datetime.now().strftime('%H:%M:%S')
        
        # Put in queue (thread-safe)
        # Don't access st.session_state from background thread!
        import queue
        try:
            # Get the queue from somewhere accessible
            # We'll store it in the processor
            if hasattr(processor, 'ui_transcript_queue'):
                processor.ui_transcript_queue.put(transcript)
                logger.info(f"✅ Queued transcript for UI: [{transcript['timestamp']}] {transcript.get('text', '')[:40]}...")
            else:
                logger.error("❌ ui_transcript_queue not found on processor!")
        except Exception as e:
            logger.error(f"❌ Could not queue transcript: {e}")
    
    try:
        # Attach queue to processor so callback can access it
        import queue
        processor.ui_transcript_queue = queue.Queue()
        logger.info(f"✅ Created ui_transcript_queue on processor (id: {id(processor)})")
        
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
