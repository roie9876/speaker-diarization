"""
Main Streamlit Application for Speaker Diarization System.

Provides a web interface with three modes:
1. Enrollment - Create speaker profiles from reference audio
2. Batch Processing - Process audio files and transcribe target speaker
3. Live Monitoring - Real-time speaker monitoring and transcription
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Set page config
st.set_page_config(
    page_title="Speaker Diarization System",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import UI components
from src.ui.enrollment_tab import render_enrollment_tab
from src.ui.batch_tab import render_batch_tab
from src.ui.live_tab import render_live_tab
from src.config.config_manager import get_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.current_profile = None
        st.session_state.batch_results = None
        st.session_state.realtime_active = False
        logger.info("Session state initialized")


def render_sidebar():
    """Render sidebar with configuration and info."""
    with st.sidebar:
        st.title("🎤 Speaker Diarization")
        st.markdown("---")
        
        # Configuration info
        try:
            config = get_config()
            
            st.subheader("⚙️ Configuration")
            st.text(f"Azure Region: {config.azure_region}")
            st.text(f"Azure Mode: {config.azure_mode}")
            st.text(f"Similarity Threshold: {config.similarity_threshold}")
            st.text(f"GPU Enabled: {config.use_gpu}")
            
            st.markdown("---")
            
            # System info
            st.subheader("📊 System Info")
            
            import torch
            if torch.backends.mps.is_available():
                st.success("✓ MPS GPU Available")
            elif torch.cuda.is_available():
                st.success("✓ CUDA GPU Available")
            else:
                st.info("ℹ️ Using CPU")
            
        except Exception as e:
            st.error(f"Configuration error: {e}")
            st.warning("Please check your .env file")
        
        st.markdown("---")
        
        # Help section
        with st.expander("❓ Help"):
            st.markdown("""
            **Quick Start:**
            1. **Enrollment**: Upload reference audio to create speaker profile
            2. **Batch**: Process files and get transcripts
            3. **Live**: Monitor and transcribe in real-time
            
            **Requirements:**
            - Azure Speech Service API key
            - Hugging Face token
            - Reference audio samples
            """)
        
        # About section
        with st.expander("ℹ️ About"):
            st.markdown("""
            **Speaker Diarization System**
            
            Version: 0.1.0
            
            Features:
            - Speaker identification using pyannote.audio
            - Selective transcription with Azure Speech
            - Cloud and container support
            - Real-time monitoring
            """)


def main():
    """Main application entry point."""
    # Initialize session state
    initialize_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Main content area
    st.title("🎤 Speaker Diarization & Selective Transcription")
    st.markdown("Identify specific speakers and transcribe only their speech")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs([
        "👤 Enrollment",
        "📁 Batch Processing",
        "🔴 Live Monitoring"
    ])
    
    with tab1:
        render_enrollment_tab()
    
    with tab2:
        render_batch_tab()
    
    with tab3:
        render_live_tab()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Application error: {e}")
        logger.error(f"Application error: {e}", exc_info=True)
        st.info("Please check logs for details")
