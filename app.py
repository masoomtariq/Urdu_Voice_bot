import pyaudio
import tf_keras as keras
import streamlit as st
import speech_recognition as sr
import pyttsx3
from transformers import pipeline
from streamlit_webrtc import webrtc_streamer


# Initialize recognizer and speaker
recognizer = sr.Recognizer()
speaker = pyttsx3.init()
speaker.setProperty('voice', 'english')  # Replace with Urdu voice if available

# Load Urdu language model
#nlp = pipeline("text-generation", model="your_urdu_model")  # Replace with your model
fill_mask = pipeline("fill-mask", model="urduhack/roberta-urdu-small", tokenizer="urduhack/roberta-urdu-small")

def speech_to_text(audio_file):
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data, language='urdu')
            return text
        except sr.UnknownValueError:
            st.error("Speech Recognition Error: Could not understand audio")
            return None

def text_to_speech(text):
    speaker.say(text)
    speaker.runAndWait()

def main():
    st.title("Urdu Voice Input and Response")

    # Record audio
    audio_file = "audio.wav"
    webrtc_streamer(key="audio_file", video=False)
    if st.button("Record Urdu Audio"):
        with sr.Microphone() as source:
            st.audio(source)
            audio = recognizer.listen(source)
            with open(audio_file, "wb") as f:
                f.write(audio.get_wav_data())

    # Process audio and generate response
    if st.button("Process"):
        text = speech_to_text(audio_file)
        if text:
            st.text_area("Input Text:", text)

            # Generate response using the language model
            response = fill_mask(text, max_length=50, num_return_sequences=1)[0]['generated_text']
            st.text_area("Generated Response:", response)

            # Convert response to speech
            text_to_speech(response)

if __name__ == "__main__":
    main()