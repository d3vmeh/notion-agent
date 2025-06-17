import speech_recognition as sr
import keyboard
import time


def listen_for_speech_push_to_talk():
    """Simple push-to-talk: Hold SPACE to record, release to stop"""
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("🎤 Push-to-Talk Mode")
        print("HOLD DOWN SPACE while talking")
        print("RELEASE SPACE when done")
        print("(Say 'quit' to exit)")
        
        print("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1.0)
        
        recognizer.energy_threshold = 100
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 0.3
        
        try:
            print("🎤 HOLD SPACE and start talking...")
            
            while not keyboard.is_pressed('space'):
                time.sleep(0.1)
            
            print("🟢 Recording... (Release SPACE to stop)")
            
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=30)
            
            print("🔄 Processing speech...")
            text = recognizer.recognize_google(audio)
            print(f"✅ You said: '{text}'")
            return text.lower()
            
        except sr.WaitTimeoutError:
            print("❌ No speech detected. Try again.")
            return None
        except sr.UnknownValueError:
            print("❌ Could not understand audio. Please try again.")
            return None
        except sr.RequestError as e:
            print(f"❌ Could not request results; {e}")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
