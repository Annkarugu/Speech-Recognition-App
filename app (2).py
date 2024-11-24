import streamlit as st
import speech_recognition as sr
import pyaudio

# Initialize the recognizer and global variables
recognizer = sr.Recognizer()
pause_flag = False
transcription = ""

# Function to handle audio transcription
def transcribe_audio(api_choice, language):
    global pause_flag, transcription
    try:
        # List all available microphones
        mic_list = sr.Microphone.list_microphone_names()
        if not mic_list:
            st.error("No microphones detected. Please check your system's microphone settings.")
            return

        # Select microphone index
        mic_index = st.sidebar.number_input("Select microphone index:", value=0, step=1, min_value=0, max_value=len(mic_list) - 1)
        st.write(f"Using microphone: {mic_list[mic_index]}")

        # Use the selected microphone
        with sr.Microphone(device_index=mic_index) as source:
            st.write("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source)
            while not pause_flag:
                st.write("Listening...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

                # Handle API choice
                if api_choice == "Google":
                    text = recognizer.recognize_google(audio, language=language)
                elif api_choice == "Sphinx":
                    text = recognizer.recognize_sphinx(audio)
                else:
                    text = "Selected API not implemented yet."

                transcription += text + "\n"

                # Update transcription in Streamlit (use session_state to store state across re-renders)
                st.session_state.transcription = transcription
                st.success(f"Transcription: {text}")

    except sr.WaitTimeoutError:
        st.warning("Listening timed out, no speech detected.")
    except sr.UnknownValueError:
        st.warning("Speech was unintelligible.")
    except Exception as e:
        st.error(f"Error: {e}")
        with open("error_log.txt", "a") as log_file:
            log_file.write(str(e) + "\n")

# Function to pause the recognition
def pause_recognition():
    global pause_flag
    pause_flag = True

# Function to resume the recognition
def resume_recognition():
    global pause_flag
    pause_flag = False

# Streamlit app structure
def main():
    st.title("Speech Recognition App")
    st.write("This app supports multiple speech recognition APIs and lets you pause/resume transcription.")

    # Sidebar for settings
    st.sidebar.header("Settings")
    api_choice = st.sidebar.selectbox("Select Speech Recognition API", ["Google", "Sphinx"])
    language = st.sidebar.text_input("Enter language code (e.g., 'en-US')", value="en-US")
    save_option = st.sidebar.checkbox("Save transcription to file")

    # Display available microphones in the sidebar
    st.sidebar.subheader("Available Microphones")
    mic_list = sr.Microphone.list_microphone_names()
    if not mic_list:
        st.error("No microphones detected. Please check your system's microphone settings.")
    else:
        for i, mic_name in enumerate(mic_list):
            st.sidebar.write(f"{i}: {mic_name}")

    # Initialize transcription state if not already set
    if 'transcription' not in st.session_state:
        st.session_state.transcription = ""

    # Display control buttons
    start_button = st.button("Start Recognition")
    pause_button = st.button("Pause Recognition")
    resume_button = st.button("Resume Recognition")
    
    # Display transcription
    st.subheader("Transcription:")
    transcription_box = st.empty()

    # Start recognition when the start button is pressed
    if start_button and not pause_flag:
        st.session_state.transcription = ""  # Reset transcription
        transcribe_audio(api_choice, language)
    
    # Pause or resume based on user input
    if pause_button:
        pause_recognition()
        st.info("Recognition paused.")
    if resume_button:
        resume_recognition()
        st.info("Recognition resumed.")

    # Display real-time transcription
    transcription_box.text_area("Live Transcription", value=st.session_state.transcription, height=300)

    # Save transcription if the option is enabled
    if save_option and st.session_state.transcription:
        with open("transcription.txt", "w") as f:
            f.write(st.session_state.transcription)
        st.success("Transcription saved to 'transcription.txt'")

if __name__ == "__main__":
    main()


