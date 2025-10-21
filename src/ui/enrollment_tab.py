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
        
        # Audio file upload
        uploaded_file = st.file_uploader(
            "Upload Reference Audio",
            type=["wav", "mp3", "m4a", "flac"],
            help="Upload a clear audio sample of the target speaker (minimum 3 seconds recommended)"
        )
        
        if uploaded_file is not None:
            # Preview audio
            st.audio(uploaded_file, format=f"audio/{uploaded_file.name.split('.')[-1]}")
            
            # Show file info
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
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
                        
                        # Create profile
                        st.info("💾 Saving profile...")
                        profile = profile_manager.create_profile(
                            name=speaker_name,
                            embedding=embedding,
                            audio_file=uploaded_file.name,
                            metadata={
                                "audio_duration": duration,
                                "file_format": uploaded_file.name.split('.')[-1]
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
                with st.expander(f"👤 {profile['name']}", expanded=False):
                    col_a, col_b = st.columns([2, 1])
                    
                    with col_a:
                        st.text(f"ID: {profile['id'][:8]}...")
                        st.text(f"Created: {profile['created_date'][:10]}")
                        
                        # Metadata
                        metadata = profile.get('metadata', {})
                        if 'audio_duration' in metadata:
                            st.text(f"Duration: {metadata['audio_duration']:.1f}s")
                        if 'audio_file' in metadata:
                            st.text(f"File: {metadata['audio_file']}")
                    
                    with col_b:
                        # Action buttons
                        if st.button("Select", key=f"select_{profile['id']}", help="Use this profile"):
                            full_profile = profile_manager.load_profile(profile['id'])
                            st.session_state.current_profile = full_profile
                            st.success(f"✓ Selected: {profile['name']}")
                        
                        if st.button("🗑️ Delete", key=f"delete_{profile['id']}", help="Delete this profile"):
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
                format_func=lambda x: next(p['name'] for p in profiles if p['id'] == x)
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
