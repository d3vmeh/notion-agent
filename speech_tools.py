import speech_recognition as sr



def listen_for_speech():
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("🎤 Listening... Speak your task now!")
        print("(Say 'quit' to exit, 'clear' to clear the screen)")
        
        # Adjust for ambient noise
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            print("Processing speech...")
            
            # Use Google's speech recognition
            text = recognizer.recognize_google(audio)
            print(f"You said: '{text}'")
            return text.lower()
            
        except sr.WaitTimeoutError:
            print("No speech detected. Please try again.")
            return None
        except sr.UnknownValueError:
            print("Could not understand audio. Please try again.")
            return None
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
