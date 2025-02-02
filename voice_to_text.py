import speech_recognition as sr
import pyttsx3
import google.generativeai as genai

def speech_to_text():
    # Initialize recognizer
    recognizer = sr.Recognizer()

    # Use the microphone as source for input
    with sr.Microphone() as source:
        print("Please speak something...")
        recognizer.adjust_for_ambient_noise(source, duration=1)  # Adjust for ambient noise
        print("Listening...")
        # Listen for the first phrase and extract it into audio data
        try:
            audio_data = recognizer.listen(source, timeout=10, phrase_time_limit=20)
            print("Recognizing...")
            # Recognize speech using Google Web Speech API
            text = recognizer.recognize_google(audio_data)
            print("You said: " + text)
            return text
        except sr.WaitTimeoutError:
            print("Listening timed out while waiting for phrase to start")
        except sr.UnknownValueError:
            print("Google Web Speech API could not understand the audio")
        except sr.RequestError as e:
            print("Could not request results from Google Web Speech API; {0}".format(e))
    return None

def get_response_from_gemini(input_text):
    # Configure the Gemini API
    genai.configure(api_key="AIzaSyA4naNwbP9-l9EkOsZ5p64udKa7gon-ClE")
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    try:
        # Add context to the input text to specify the travel agency role and request a concise, casual response
        prompt = f"As a customer service representative of a travel agency, respond concisely and casually to the following query: {input_text}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error: Could not get response from API - {e}")
        return None

def text_to_speech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

if __name__ == "__main__":
    # Welcome message
    welcome_message = "Welcome to the travel agency customer service. How can I assist you with your travel plans today?"
    print(welcome_message)
    text_to_speech(welcome_message)
    
    while True:
        input_text = speech_to_text()
        if input_text:
            response_text = get_response_from_gemini(input_text)
            if response_text:
                print("Response: " + response_text)
                text_to_speech(response_text)