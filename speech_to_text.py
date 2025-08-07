#!/usr/bin/env python3
"""
🎤 Speech-to-Text Module for Gemma 3n Multiverse
Handles voice input processing with multiple fallback options
"""

import speech_recognition as sr
import threading
import time
from typing import Optional, Callable, Dict, Any
import streamlit as st

class SpeechToTextManager:
    """Manages speech-to-text functionality with multiple engines"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.is_listening = False
        self.audio_callback = None
        self.recognition_thread = None
        
        # Try to initialize microphone
        try:
            self.microphone = sr.Microphone()
            # Adjust for ambient noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("🎤 Microphone initialized successfully")
        except Exception as e:
            print(f"⚠️ Microphone initialization failed: {e}")
            self.microphone = None
    
    def is_microphone_available(self) -> bool:
        """Check if microphone is available"""
        return self.microphone is not None
    
    def get_microphone_list(self) -> list:
        """Get list of available microphones"""
        try:
            return sr.Microphone.list_microphone_names()
        except Exception:
            return []
    
    def start_continuous_listening(self, callback: Callable[[str], None]):
        """Start continuous speech recognition in background"""
        if not self.microphone:
            raise Exception("Microphone not available")
        
        self.audio_callback = callback
        self.is_listening = True
        
        def listen_continuously():
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
            
            while self.is_listening:
                try:
                    # Listen for phrase with timeout
                    with self.microphone as source:
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    
                    # Try to recognize speech
                    try:
                        text = self.recognizer.recognize_google(audio)
                        if text.strip() and self.audio_callback:
                            self.audio_callback(text)
                    except sr.UnknownValueError:
                        # Speech was unintelligible
                        pass
                    except sr.RequestError as e:
                        print(f"🚫 Speech recognition error: {e}")
                        # Fallback to offline recognition
                        try:
                            text = self.recognizer.recognize_sphinx(audio)
                            if text.strip() and self.audio_callback:
                                self.audio_callback(text)
                        except:
                            pass
                
                except sr.WaitTimeoutError:
                    # No speech detected, continue listening
                    pass
                except Exception as e:
                    print(f"🚫 Listening error: {e}")
                    time.sleep(0.1)
        
        self.recognition_thread = threading.Thread(target=listen_continuously, daemon=True)
        self.recognition_thread.start()
    
    def stop_listening(self):
        """Stop continuous listening"""
        self.is_listening = False
        if self.recognition_thread:
            self.recognition_thread.join(timeout=2)
    
    def recognize_once(self, timeout: int = 5) -> Optional[str]:
        """Recognize speech once with timeout"""
        if not self.microphone:
            raise Exception("Microphone not available")
        
        try:
            with self.microphone as source:
                print("🎤 Listening...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            print("🔄 Processing speech...")
            
            # Try Google first (requires internet)
            try:
                text = self.recognizer.recognize_google(audio)
                print(f"✅ Google recognition: {text}")
                return text
            except sr.RequestError:
                print("⚠️ Google recognition failed, trying offline...")
                
            # Fallback to offline Sphinx
            try:
                text = self.recognizer.recognize_sphinx(audio)
                print(f"✅ Sphinx recognition: {text}")
                return text
            except:
                print("❌ Sphinx recognition failed")
                
            return None
            
        except sr.WaitTimeoutError:
            print("⏰ No speech detected within timeout")
            return None
        except Exception as e:
            print(f"🚫 Recognition error: {e}")
            return None
    
    def recognize_from_file(self, audio_file_path: str) -> Optional[str]:
        """Recognize speech from audio file"""
        try:
            with sr.AudioFile(audio_file_path) as source:
                audio = self.recognizer.record(source)
            
            # Try Google first
            try:
                return self.recognizer.recognize_google(audio)
            except sr.RequestError:
                # Fallback to Sphinx
                return self.recognizer.recognize_sphinx(audio)
                
        except Exception as e:
            print(f"🚫 File recognition error: {e}")
            return None

class StreamlitSpeechInterface:
    """Streamlit-specific speech interface"""
    
    def __init__(self):
        self.stt_manager = SpeechToTextManager()
        
    def render_speech_interface(self) -> Optional[str]:
        """Render speech-to-text interface in Streamlit"""
        st.markdown("### 🎤 Voice Input")
        
        # Check microphone availability
        if not self.stt_manager.is_microphone_available():
            st.error("🚫 Microphone not available. Please check your audio settings.")
            
            # Show troubleshooting
            with st.expander("🔧 Microphone Troubleshooting", expanded=True):
                st.markdown("""
                **Common Issues & Solutions:**
                
                1. **Permissions**
                   - Allow microphone access in your browser
                   - Check system microphone permissions
                
                2. **Hardware**
                   - Ensure microphone is connected and working
                   - Test microphone in other applications
                
                3. **Dependencies**
                   - Install: `pip install pyaudio speechrecognition`
                   - On Mac: `brew install portaudio`
                   - On Ubuntu: `sudo apt-get install python3-pyaudio`
                
                4. **Alternative**
                   - Use the audio file upload below
                """)
            
            # Audio file upload as fallback
            st.markdown("### 📁 Audio File Upload")
            audio_file = st.file_uploader(
                "Upload audio file for speech recognition",
                type=['wav', 'mp3', 'flac', 'm4a'],
                help="Upload an audio file to convert speech to text"
            )
            
            if audio_file:
                # Save uploaded file temporarily
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(audio_file.getbuffer())
                    tmp_path = tmp_file.name
                
                try:
                    with st.spinner("🔄 Processing audio..."):
                        recognized_text = self.stt_manager.recognize_from_file(tmp_path)
                    
                    if recognized_text:
                        st.success(f"✅ Recognized: {recognized_text}")
                        return recognized_text
                    else:
                        st.error("❌ Could not recognize speech from audio file")
                        
                finally:
                    # Clean up temp file
                    os.unlink(tmp_path)
            
            return None
        
        # Microphone available - show controls
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.info("🎤 Microphone ready! Click to start voice input.")
        
        with col2:
            if st.button("🎤 Start Recording", key="start_recording"):
                return self._handle_voice_recording()
        
        with col3:
            # Show available microphones
            mics = self.stt_manager.get_microphone_list()
            if mics:
                selected_mic = st.selectbox(
                    "Microphone",
                    range(len(mics)),
                    format_func=lambda x: mics[x][:30] + "..." if len(mics[x]) > 30 else mics[x],
                    key="mic_selector"
                )
        
        # Voice activation settings
        with st.expander("⚙️ Voice Settings", expanded=False):
            st.markdown("**Recognition Settings:**")
            
            col1, col2 = st.columns(2)
            with col1:
                timeout = st.slider("Timeout (seconds)", 1, 10, 5, key="voice_timeout")
            with col2:
                st.checkbox("Continuous listening", key="continuous_voice", 
                           help="Keep listening for voice commands")
            
            st.markdown("**Tips for better recognition:**")
            st.markdown("""
            - Speak clearly and at normal pace
            - Minimize background noise
            - Use short, clear phrases
            - Ensure good microphone positioning
            """)
        
        return None
    
    def _handle_voice_recording(self) -> Optional[str]:
        """Handle voice recording with progress indicator"""
        try:
            with st.spinner("🎤 Listening... Speak now!"):
                # Create progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Update progress during recording
                for i in range(50):  # 5 seconds max
                    progress_bar.progress((i + 1) / 50)
                    status_text.text(f"Recording... {5 - i//10}s remaining")
                    time.sleep(0.1)
                
                # Recognize speech
                status_text.text("🔄 Processing speech...")
                recognized_text = self.stt_manager.recognize_once(timeout=5)
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
                
                if recognized_text:
                    st.success(f"✅ You said: {recognized_text}")
                    return recognized_text
                else:
                    st.warning("⚠️ No speech detected or recognition failed")
                    return None
                    
        except Exception as e:
            st.error(f"🚫 Voice recording error: {str(e)}")
            return None

# Global speech interface instance
speech_interface = StreamlitSpeechInterface()