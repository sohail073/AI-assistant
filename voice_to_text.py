import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
import pandas as pd
import os
import openpyxl  # Add this import
import re  # Add this import
from dotenv import load_dotenv  # Add this import

# Load environment variables from .env file
load_dotenv()

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
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
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

def extract_numeric_value(text):
    match = re.search(r'\d+', text)
    return match.group() if match else None

def is_positive_response(response):
    positive_responses = ["yes", "yeah", "yup", "sure", "i do", "i have"]
    return any(phrase in response.lower() for phrase in positive_responses)

def suggest_plans(budget):
    # Dummy plans for demonstration purposes
    plans = [
        {"Destination": "Paris", "Budget": "2000", "Description": "A romantic getaway in Paris."},
        {"Destination": "New York", "Budget": "1500", "Description": "Explore the bustling city of New York."},
        {"Destination": "Tokyo", "Budget": "2500", "Description": "Experience the vibrant culture of Tokyo."}
    ]
    suggested_plans = [plan for plan in plans if int(plan["Budget"]) <= int(budget)]
    return suggested_plans

def gather_customer_info():
    info = {}
    questions = {
        "Name": "May I have your name, please?",
        "Contact_number": "Can you provide your contact number?",
        "Destination": "Where would you like to travel?",
        "Number_of_people": "How many people will be traveling?",
        "Budget": "What is your budget for this trip?"
    }
    
    # Greet and introduce services
    text_to_speech("Welcome to our travel agency. We offer flight bookings, hotel inquiries, and travel packages.")
    print("Welcome to our travel agency. We offer flight bookings, hotel inquiries, and travel packages.")
    
    # Identify user intent
    text_to_speech("What do you need help with today?")
    print("What do you need help with today?")
    response = speech_to_text()
    if response:
        info["Intent"] = response
    else:
        text_to_speech("Sorry, I didn't catch that. Could you please repeat?")
        print("Sorry, I didn't catch that. Could you please repeat?")
        response = speech_to_text()
        if response:
            info["Intent"] = response
        else:
            text_to_speech("Sorry, I couldn't understand you. Let's move to the next question.")
            print("Sorry, I couldn't understand you. Let's move to the next question.")
            info["Intent"] = "N/A"
    
    # Assist with booking or offer recommendations
    if is_positive_response(info["Intent"]):
        for key, question in questions.items():
            text_to_speech(question)
            print(question)
            response = speech_to_text()
            if response:
                info[key] = response
            else:
                text_to_speech("Sorry, I didn't catch that. Could you please repeat?")
                print("Sorry, I didn't catch that. Could you please repeat?")
                response = speech_to_text()
                if response:
                    info[key] = response
                else:
                    text_to_speech("Sorry, I couldn't understand you. Let's move to the next question.")
                    print("Sorry, I couldn't understand you. Let's move to the next question.")
                    info[key] = "N/A"
    else:
        text_to_speech("I have some suggestions for you based on your budget.")
        print("I have some suggestions for you based on your budget.")
        text_to_speech("What is your budget for this trip?")
        print("What is your budget for this trip?")
        budget_response = speech_to_text()
        budget_value = extract_numeric_value(budget_response) if budget_response else None
        if budget_value:
            info["Budget"] = budget_value
            suggested_plans = suggest_plans(budget_value)
            if suggested_plans:
                for plan in suggested_plans:
                    text_to_speech(f"{plan['Description']} to {plan['Destination']} within a budget of {plan['Budget']} dollars.")
                    print(f"{plan['Description']} to {plan['Destination']} within a budget of {plan['Budget']} dollars.")
                    info["Destination"] = plan["Destination"]
                    break  # Suggest only one plan for simplicity
            else:
                text_to_speech("Sorry, we don't have any plans within your budget.")
                print("Sorry, we don't have any plans within your budget.")
        else:
            text_to_speech("Sorry, I couldn't understand your budget. Let's move to the next question.")
            print("Sorry, I couldn't understand your budget. Let's move to the next question.")
            info["Budget"] = "N/A"
        
        for key in ["Name", "Contact_number", "Number_of_people"]:
            text_to_speech(questions[key])
            print(questions[key])
            response = speech_to_text()
            if response:
                info[key] = response
            else:
                text_to_speech("Sorry, I didn't catch that. Could you please repeat?")
                print("Sorry, I didn't catch that. Could you please repeat?")
                response = speech_to_text()
                if response:
                    info[key] = response
                else:
                    text_to_speech("Sorry, I couldn't understand you. Let's move to the next question.")
                    print("Sorry, I couldn't understand you. Let's move to the next question.")
                    info[key] = "N/A"
    
    return info

def save_to_file(info):
    file_path = "user_info.txt"
    with open(file_path, "a") as file:
        file.write(",".join(info.values()) + "\n")
    print("Customer information saved successfully.")

if __name__ == "__main__":
    
    while True:
        customer_info = gather_customer_info()
        save_to_file(customer_info)
        text_to_speech("Thank you for providing your information. We will get back to you shortly.")
        print("Thank you for providing your information. We will get back to you shortly.")
        break  # Remove or modify this line if you want to continue gathering information in a loop