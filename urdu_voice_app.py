import streamlit as st
import speech_recognition as sr
from audio_recorder_streamlit import audio_recorder
import base64
import tempfile
import google.generativeai as genai
from gtts import gTTS
from dotenv import load_dotenv
import os

load_dotenv()

#GEMINI_API_KEY = os.getenv('GOOGLE_API_KEY')
#GEMINI_API_KEY = os.environ.get('API_KEY')


GEMINI_API_KEY = st.secrets['GEMINI_API_KEY']

genai.configure(api_key=GEMINI_API_KEY)

def main():
    st.title("Urdu Voice Chatbot")
    
    st.sidebar.title('''About this App''')
    st.sidebar.info(f'''This a Urdu voice chatbot created using Streamlit. It takes in Urdu voice input and response in Urdu voice''')

    st.sidebar.write("")  # Adds one line of space
    st.sidebar.write("")  # Adds one line of space

    
    st.sidebar.write("Developed by :blue[Masoom Tariq]")

    urdu_recorder = audio_recorder(text='بولیۓ', icon_size="1x", icon_name="microphone-lines", key="urdu_recorder")

    if urdu_recorder is not None:
        
        with st.container():
            col1, col2 = st.columns(2)

            with col1:
                # Display the audio file                                                                                                                                                                                                                                                                                                                                                                                                                                                         
                st.audio(urdu_recorder)

                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_recording:
                    temp_recording.write(urdu_recorder)
                    temp_recording_path = temp_recording.name
                
                # Convert audio file to text
                
                text = Urdu_audio_to_text(temp_recording_path)
                #st.success( text)

                # Remove the temporary file
                os.remove(temp_recording_path)


        response_text = llmModelResponse(text)

        with st.container():
            col1, col2 = st.columns(2)

            with col2:
                # Convert the response text to speech
                response_audio_html = response_to_urdu_audio(response_text)
                st.info(response_text)

                st.markdown(response_audio_html, unsafe_allow_html=True)
                #tts = gTTS(text = response_text, lang = 'ur')
                #st.audio(tts.get_bytes(), format="audio/mp3")


def Urdu_audio_to_text(temp_recording_path):
    # Speech Recognition
    recognizer = sr.Recognizer()
    with sr.AudioFile(temp_recording_path) as source:
        urdu_recoded_voice = recognizer.record(source)
        try:
            text = recognizer.recognize_google(urdu_recoded_voice, language="ur")
            return text
        except sr.UnknownValueError:
            return "آپ کی آواز واضح نہیں ہے"
        except sr.RequestError:
            return "Sorry, my speech service is down"

def response_to_urdu_audio(text, lang='ur'):
    tts = gTTS(text=text, lang=lang)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete = False) as temp_audio:
        tts_audio_path = temp_audio.name
    #tts_audio_path = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False).name
        tts.save(tts_audio_path)

    # Get the base64 string of the audio file
    audio_base64 = get_audio_base64(tts_audio_path)
    os.remove(tts_audio_path)

    # Autoplay audio using HTML and JavaScript
    audio_html = f"""
    <audio controls autoplay>
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        Your browser does not support the audio element.
    </audio>
    """
    return audio_html

#@st.cache
def get_audio_base64(tts_audio_path):
    with open(tts_audio_path, 'rb') as audio_file:
        audio_bytes = audio_file.read()
        audio_base64 = base64.b64encode(audio_bytes).decode()
    return audio_base64

def llmModelResponse(text):
    prompt = f"""Kindly answer this question in Urdu langauge. 
    Dont use any other language or chaaracters from other languages.
    Use some kind Urdu words in start and ending of your answer realted to question. 
    Keep your answer short. 
    You can also ask anything related to the topic in urdu.
    if you dont know the answer or dont understand the question, 
    Respond with 'I did not get what you speak, please try again' in urdu.
    Question: {text}"""

    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
   
    )

    chat_session = model.start_chat()
    response = chat_session.send_message(prompt)

    return response.text

if __name__ == "__main__":
    main()
