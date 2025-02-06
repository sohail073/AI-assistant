import speech_recognition as sr
import pyttsx3
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import time
from fuzzywuzzy import fuzz

load_dotenv()

class VoiceEngine:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 175)  # Slower rate for clarity
        self.engine.setProperty('volume', 0.9)  # Slightly lower volume
        self.recognizer = sr.Recognizer()

    def speak(self, text, pause=0.5):  # Reduce pause time
        print(f"\nAgent: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
        time.sleep(pause)  # Shorter pause after speaking

    def listen(self, timeout=8):
        with sr.Microphone() as source:
            print("\nListening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(source, timeout=timeout)
                text = self.recognizer.recognize_google(audio)
                print(f"Customer: {text}")
                return text.lower()
            except (sr.UnknownValueError, sr.RequestError, sr.WaitTimeoutError):
                return None

class TravelAgent:
    def __init__(self):
        self.voice = VoiceEngine()
        self.lead_info = {}
        self.no_count = 0  # Track the number of NO responses
        
        # Sample travel deals
        self.hot_deals = {
            "budget": {
                "destination": "Bali",
                "price": 899,
                "includes": "flights and 4-star hotel"
            },
            "standard": {
                "destination": "Dubai",
                "price": 1499,
                "includes": "flights, 5-star hotel, and desert safari"
            },
            "luxury": {
                "destination": "Maldives",
                "price": 2499,
                "includes": "business class flights and water villa"
            }
        }

    def is_positive_response(self, response):
        if not response:
            return False
        positive_words = ['yes', 'yeah', 'sure', 'okay', 'fine', 'yep', 'yup', 'interested']
        return any(fuzz.partial_ratio(word, response) > 80 for word in positive_words)

    def handle_introduction(self):
        self.voice.speak("Hey! This is Jack from Dream Vacations! We're offering exclusive travel deals this season. Would you like to hear about them?")
        response = self.voice.listen()
        
        if self.is_positive_response(response):
            return self.handle_travel_inquiry()
        else:
            self.no_count += 1
            if self.no_count >= 2:
                self.voice.speak("I understand! Would you like me to send you our best deals via WhatsApp instead?")
                contact_preference = self.voice.listen()
                if contact_preference:
                    self.lead_info['contact_preference'] = contact_preference
                    self.voice.speak("Great! Our travel expert will reach out to you soon with our best deals. Have a wonderful day!")
                else:
                    self.voice.speak("Thank you for your time. Have a great day!")
                return False
            else:
                self.voice.speak("No worries! Would you like me to send you travel deals via WhatsApp or Email instead?")
                contact_preference = self.voice.listen()
                if contact_preference:
                    self.lead_info['contact_preference'] = contact_preference
                    self.voice.speak("Great! Our travel expert will reach out to you soon with our best deals. Have a wonderful day!")
                return False

    def handle_travel_inquiry(self):
        # Destination inquiry
        self.voice.speak("Great! Do you already have a destination in mind, or would you like some suggestions?")
        response = self.voice.listen()
        
        if response and 'suggest' in response:
            return self.suggest_destinations()
        elif response:
            self.lead_info['preferred_destination'] = response
            return self.collect_travel_details()
        
        return self.suggest_destinations()

    def suggest_destinations(self):
        self.voice.speak("Based on popular choices, I can suggest three amazing destinations. We have Bali with pristine beaches, Dubai for luxury shopping and desert adventures, or the Maldives for ultimate relaxation. Which interests you most?")
        response = self.voice.listen()
        
        if response:
            self.lead_info['interested_destination'] = response
            return self.collect_travel_details()
        return False

    def collect_travel_details(self):
        questions = {
            'travel_dates': "When do you plan to travel?",
            'travelers': "How many people will be traveling with you?",
            'budget': "What is your preferred budget for this trip?"
        }

        for key, question in questions.items():
            self.voice.speak(question)
            response = self.voice.listen()
            while not response:
                self.voice.speak("Sorry, I didn't catch that. Could you please repeat?")
                response = self.voice.listen()
            self.lead_info[key] = response

        return self.present_offers()

    def present_offers(self):
        # Simplified deal matching based on collected info
        deal = self.hot_deals['standard']  # Default to standard deal
        
        self.voice.speak(f"I found a great deal for {deal['destination']} at ${deal['price']} including {deal['includes']}. Shall I book it for you?")
        response = self.voice.listen()
        
        if self.is_positive_response(response):
            return self.handle_booking_details()
        else:
            self.no_count += 1
            if self.no_count >= 2:
                self.voice.speak("I understand! Would you like me to send you our best deals via WhatsApp instead?")
                contact_preference = self.voice.listen()
                if contact_preference:
                    self.lead_info['contact_preference'] = contact_preference
                    self.voice.speak("Great! Our travel expert will reach out to you soon with our best deals. Have a wonderful day!")
                else:
                    self.voice.speak("Thank you for your time. Have a great day!")
                return False
            else:
                self.voice.speak("Would you like to hear about other available deals?")
                response = self.voice.listen()
                if self.is_positive_response(response):
                    return self.present_alternative_offers()
        return False

    def handle_booking_details(self):
        questions = [
            "Would you prefer economy, business, or first-class flights?",
            "Do you need hotel accommodations as well?",
            "Would you like to add travel insurance or visa assistance to your trip?",
            "Are you interested in exclusive tour packages for your destination?"
        ]

        for question in questions:
            self.voice.speak(question)
            response = self.voice.listen()
            while not response:
                self.voice.speak("Sorry, I didn't catch that. Could you please repeat?")
                response = self.voice.listen()
            self.lead_info[question] = response

        return self.handle_closing()

    def present_alternative_offers(self):
        self.voice.speak("We also have special deals for Dubai and the Maldives. Would you like to hear about these destinations?")
        response = self.voice.listen()
        
        if self.is_positive_response(response):
            return self.handle_booking_details()
        return self.handle_closing()

    def handle_closing(self):
        self.voice.speak("Shall I send these details to you via WhatsApp, Email, or SMS?")
        response = self.voice.listen()
        while not response:
            self.voice.speak("Sorry, I didn't catch that. Could you please repeat?")
            response = self.voice.listen()
        
        self.voice.speak("Would you like to speak with a travel expert for more personalized options?")
        expert_response = self.voice.listen()
        while not expert_response:
            self.voice.speak("Sorry, I didn't catch that. Could you please repeat?")
            expert_response = self.voice.listen()
        
        if self.is_positive_response(expert_response):
            self.voice.speak("I'll have our travel expert call you back within 2 hours. Thank you for your time!")
            self.lead_info['requires_callback'] = True
        else:
            self.voice.speak("Would you prefer I call you back at a more convenient time?")
            callback_response = self.voice.listen()
            while not callback_response:
                self.voice.speak("Sorry, I didn't catch that. Could you please repeat?")
                callback_response = self.voice.listen()
            if self.is_positive_response(callback_response):
                self.lead_info['callback_requested'] = True
                self.voice.speak("Perfect! Our travel expert will call you back. Have a great day!")
            else:
                self.voice.speak("Thank you for your time. Have a wonderful day!")
        
        self.save_lead()
        return False

    def save_lead(self):
        self.lead_info['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open('travel_leads.json', 'a') as f:
                json.dump(self.lead_info, f)
                f.write('\n')
        except Exception as e:
            print(f"Error saving lead: {e}")

def main():
    agent = TravelAgent()
    agent.handle_introduction()

if __name__ == "__main__":
    main()