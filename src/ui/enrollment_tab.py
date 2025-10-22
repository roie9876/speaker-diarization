"""
Enrollment Tab for Streamlit UI.

Allows users to create and manage speaker profiles from reference audio.
"""

import streamlit as st
from pathlib import Path
import tempfile

from src.services.profile_manager import ProfileManager
from src.services.identification_service import IdentificationService
from src.utils.audio_utils import validate_audio_file, get_audio_duration
from src.utils.logger import get_logger

logger = get_logger(__name__)


def render_enrollment_tab():
    """Render the speaker enrollment interface."""
    st.header("👤 Speaker Enrollment")
    st.markdown("Create a speaker profile from reference audio samples")
    
    # Initialize services
    if 'profile_manager' not in st.session_state:
        st.session_state.profile_manager = ProfileManager()
    
    if 'identification_service' not in st.session_state:
        st.session_state.identification_service = IdentificationService()
    
    profile_manager = st.session_state.profile_manager
    identification = st.session_state.identification_service
    
    # Two columns: Create Profile | Manage Profiles
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Create New Profile")
        
        # Speaker name input
        speaker_name = st.text_input(
            "Speaker Name",
            placeholder="e.g., John Doe",
            help="Enter the name of the person you want to identify"
        )
        
        # Audio input method selection
        audio_input_method = st.radio(
            "Audio Input Method",
            options=["Upload File", "Record from Microphone"],
            horizontal=True,
            help="Choose how to provide reference audio"
        )
        
        uploaded_file = None
        temp_path = None
        duration = None
        file_extension = None
        
        if audio_input_method == "Upload File":
            # Audio file upload
            uploaded_file = st.file_uploader(
                "Upload Reference Audio",
                type=["wav", "mp3", "m4a", "flac"],
                help="Upload a clear audio sample of the target speaker (minimum 3 seconds recommended)"
            )
        else:
            # Microphone recording
            st.markdown("**🎤 Record from Microphone**")
            st.info("Speak clearly for 5-10 seconds. Longer recordings work better!")
            
            # Use Streamlit's audio_input (available in recent versions)
            recorded_audio = st.audio_input("Record your voice")
            
            if recorded_audio is not None:
                uploaded_file = recorded_audio  # Treat recorded audio same as uploaded file
                st.success("✓ Recording captured!")
        
        # Process audio (uploaded or recorded)
        if uploaded_file is not None:
            # Preview audio
            file_extension = uploaded_file.name.split('.')[-1] if hasattr(uploaded_file, 'name') and '.' in uploaded_file.name else 'wav'
            st.audio(uploaded_file, format=f"audio/{file_extension}")
            
            # Show file info
            suffix = f".{file_extension}" if file_extension else ".wav"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                temp_path = Path(tmp_file.name)
            
            try:
                if validate_audio_file(temp_path):
                    duration = get_audio_duration(temp_path)
                    st.info(f"📊 Duration: {duration:.1f}s")
                    
                    if duration < 3.0:
                        st.warning("⚠️ Audio is short. Longer samples (>5s) work better.")
                else:
                    st.error("❌ Invalid audio file")
                    temp_path.unlink()
                    return
                    
            except Exception as e:
                st.error(f"Error validating audio: {e}")
                temp_path.unlink()
                return
        
        # Create profile button
        if st.button("Create Profile", type="primary", disabled=not speaker_name or uploaded_file is None):
            if speaker_name and uploaded_file:
                with st.spinner("Creating speaker profile..."):
                    try:
                        # Extract embedding
                        st.info("🔍 Extracting speaker embedding...")
                        embedding = identification.extract_embedding(temp_path)
                        
                        # Assess profile quality
                        st.info("📊 Assessing profile quality...")
                        quality_result = identification.assess_profile_quality(
                            audio_file=temp_path,
                            embedding=embedding
                        )
                        
                        # Display quality assessment
                        st.markdown("### Quality Assessment")
                        
                        # Overall quality with large emoji and score
                        col_q1, col_q2, col_q3 = st.columns([1, 2, 2])
                        with col_q1:
                            st.markdown(f"## {quality_result['quality_emoji']}")
                        with col_q2:
                            st.metric("Overall Quality", quality_result['quality_label'])
                        with col_q3:
                            st.metric("Quality Score", f"{quality_result['overall_score']:.2f}")
                        
                        # Detailed scores
                        st.markdown("**Component Scores:**")
                        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                        with col_s1:
                            st.metric("Duration", f"{quality_result['duration_score']:.2f}")
                        with col_s2:
                            st.metric("Audio Level", f"{quality_result['audio_level_score']:.2f}")
                        with col_s3:
                            st.metric("Embedding", f"{quality_result['embedding_score']:.2f}")
                        with col_s4:
                            st.metric("SNR", f"{quality_result['snr_score']:.2f}")
                        
                        # Show recommendations
                        if quality_result['recommendations']:
                            st.markdown("**Recommendations:**")
                            for rec in quality_result['recommendations']:
                                st.markdown(f"- {rec}")
                        
                        # Show detailed metrics in expander
                        with st.expander("📋 Detailed Metrics"):
                            details = quality_result['details']
                            st.json(details)
                        
                        # Create profile
                        st.info("💾 Saving profile...")
                        audio_filename = uploaded_file.name if hasattr(uploaded_file, 'name') else f"recorded_audio_{speaker_name}.wav"
                        profile = profile_manager.create_profile(
                            name=speaker_name,
                            embedding=embedding,
                            audio_file=audio_filename,
                            metadata={
                                "audio_duration": duration,
                                "file_format": file_extension,
                                "source": audio_input_method,
                                "quality": quality_result  # Store quality info
                            }
                        )
                        
                        # Clean up temp file
                        temp_path.unlink()
                        
                        st.success(f"✅ Profile created successfully!")
                        st.info(f"Profile ID: `{profile['id']}`")
                        
                        # Store in session state
                        st.session_state.current_profile = profile
                        
                        # Rerun to refresh profile list
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Failed to create profile: {e}")
                        logger.error(f"Profile creation failed: {e}")
                        if temp_path.exists():
                            temp_path.unlink()
    
    with col2:
        st.subheader("Manage Profiles")
        
        # Get all profiles
        profiles = profile_manager.list_profiles()
        
        if not profiles:
            st.info("📝 No profiles yet. Create one on the left!")
        else:
            st.success(f"📚 {len(profiles)} profile(s) available")
            
            # Search profiles
            search_query = st.text_input(
                "🔍 Search profiles",
                placeholder="Type to search..."
            )
            
            # Filter profiles
            if search_query:
                filtered_profiles = [
                    p for p in profiles
                    if search_query.lower() in p["name"].lower()
                ]
            else:
                filtered_profiles = profiles
            
            # Display profiles
            for profile in filtered_profiles:
                # Get quality info if available
                quality_info = profile.get('quality', {})
                quality_emoji = quality_info.get('quality_emoji', '📊')
                quality_label = quality_info.get('quality_label', '')
                
                # Include quality in expander title if available
                title = f"{quality_emoji} {profile['name']}"
                if quality_label:
                    title += f" - {quality_label}"
                
                with st.expander(title, expanded=False):
                    # Profile Info Section
                    st.markdown("### 📋 Profile Information")
                    col_info1, col_info2 = st.columns(2)
                    
                    with col_info1:
                        st.text(f"ID: {profile['id'][:8]}...")
                        st.text(f"Created: {profile['created_date'][:10]}")
                    
                    with col_info2:
                        # Metadata
                        metadata = profile.get('metadata', {})
                        if 'audio_duration' in metadata:
                            st.text(f"Duration: {metadata['audio_duration']:.1f}s")
                        if 'audio_file' in metadata:
                            st.text(f"File: {metadata['audio_file']}")
                    
                    # Quality Assessment Section
                    if quality_info:
                        st.markdown("---")
                        st.markdown("### 📊 Quality Assessment")
                        
                        # Overall quality with large display
                        col_q1, col_q2, col_q3 = st.columns([1, 2, 2])
                        with col_q1:
                            st.markdown(f"<div style='font-size: 48px; text-align: center;'>{quality_info.get('quality_emoji', '📊')}</div>", unsafe_allow_html=True)
                        with col_q2:
                            st.metric("Quality", quality_info.get('quality_label', 'Unknown'))
                        with col_q3:
                            st.metric("Score", f"{quality_info.get('overall_score', 0):.2f}")
                        
                        # Visual quality bar
                        overall_score = quality_info.get('overall_score', 0)
                        progress_color = "green" if overall_score >= 0.8 else "orange" if overall_score >= 0.65 else "red"
                        st.progress(overall_score, text=f"Overall Quality: {overall_score:.0%}")
                        
                        # Component scores
                        if 'duration_score' in quality_info:
                            st.markdown("**Component Scores:**")
                            col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                            with col_s1:
                                st.metric("Duration", f"{quality_info['duration_score']:.2f}", 
                                         help="Audio length quality (30-60s ideal)")
                            with col_s2:
                                st.metric("Audio Level", f"{quality_info['audio_level_score']:.2f}",
                                         help="Volume and clipping check")
                            with col_s3:
                                st.metric("Embedding", f"{quality_info['embedding_score']:.2f}",
                                         help="Voice fingerprint quality")
                            with col_s4:
                                st.metric("SNR", f"{quality_info['snr_score']:.2f}",
                                         help="Signal-to-noise ratio")
                        
                        # Detailed metrics
                        details = quality_info.get('details', {})
                        if details:
                            with st.expander("🔍 Detailed Metrics", expanded=False):
                                col_d1, col_d2 = st.columns(2)
                                with col_d1:
                                    if 'duration_seconds' in details:
                                        st.text(f"Duration: {details['duration_seconds']:.1f}s")
                                    if 'rms_level' in details:
                                        st.text(f"RMS Level: {details['rms_level']:.3f}")
                                    if 'peak_level' in details:
                                        st.text(f"Peak Level: {details['peak_level']:.3f}")
                                with col_d2:
                                    if 'snr_estimate_db' in details:
                                        st.text(f"SNR: {details['snr_estimate_db']:.1f} dB")
                                    if 'embedding_norm' in details:
                                        st.text(f"Embedding Norm: {details['embedding_norm']:.3f}")
                                    if 'embedding_std' in details:
                                        st.text(f"Embedding Std: {details['embedding_std']:.3f}")
                        
                        # Recommendations
                        recommendations = quality_info.get('recommendations', [])
                        if recommendations:
                            st.markdown("**💡 Recommendations:**")
                            for rec in recommendations:
                                st.caption(rec)
                    else:
                        st.info("ℹ️ Quality information not available for this profile. Re-create the profile to assess quality.")
                    
                    # Action buttons at the bottom
                    st.markdown("---")
                    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
                    
                    with col_btn1:
                        if st.button("✅ Select", key=f"select_{profile['id']}", help="Use this profile", use_container_width=True):
                            full_profile = profile_manager.load_profile(profile['id'])
                            st.session_state.current_profile = full_profile
                            st.success(f"✓ Selected: {profile['name']}")
                    
                    with col_btn2:
                        if st.button("� Export", key=f"export_{profile['id']}", help="Export this profile", use_container_width=True):
                            try:
                                output_path = profile_manager.config.results_dir / f"profile_{profile['name'].replace(' ', '_')}.json"
                                profile_manager.export_profile(profile['id'], output_path)
                                st.success(f"Exported to: {output_path.name}")
                            except Exception as e:
                                st.error(f"Export failed: {e}")
                    
                    with col_btn3:
                        if st.button("�🗑️ Delete", key=f"delete_{profile['id']}", help="Delete this profile", use_container_width=True):
                            if profile_manager.delete_profile(profile['id']):
                                st.success(f"Deleted: {profile['name']}")
                                st.rerun()
                            else:
                                st.error("Failed to delete profile")
            
            # Export/Import section
            st.markdown("---")
            st.subheader("📤 Export / Import")
            
            # Export
            profile_to_export = st.selectbox(
                "Export Profile",
                options=[p['id'] for p in profiles],
                format_func=lambda x: next(p['name'] for p in profiles if p['id'] == x),
                key="enrollment_export_profile"
            )
            
            if st.button("Export Profile"):
                try:
                    output_path = profile_manager.config.results_dir / f"profile_{profile_to_export[:8]}.json"
                    profile_manager.export_profile(profile_to_export, output_path)
                    st.success(f"Exported to: {output_path}")
                    
                    # Download button
                    with open(output_path, 'r') as f:
                        st.download_button(
                            "Download Profile",
                            f.read(),
                            file_name=f"profile_{profile_to_export[:8]}.json",
                            mime="application/json"
                        )
                except Exception as e:
                    st.error(f"Export failed: {e}")
            
            # Import
            st.markdown("**Import Profile:**")
            import_file = st.file_uploader(
                "Upload Profile JSON",
                type=["json"],
                key="profile_import"
            )
            
            if import_file is not None:
                if st.button("Import Profile"):
                    try:
                        # Save to temp file
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
                            tmp.write(import_file.getvalue())
                            tmp_path = Path(tmp.name)
                        
                        # Import
                        imported_profile = profile_manager.import_profile(tmp_path)
                        tmp_path.unlink()
                        
                        st.success(f"✅ Imported: {imported_profile['name']}")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Import failed: {e}")
    
    # Show current selected profile at bottom
    if st.session_state.current_profile:
        st.markdown("---")
        st.info(f"🎯 **Current Profile:** {st.session_state.current_profile['name']}")
