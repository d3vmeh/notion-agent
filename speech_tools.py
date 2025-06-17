import speech_recognition as sr
import time
import threading
import queue
            


def listen_for_speech_push_to_talk():
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("🎤 Push-to-Talk Mode")
        print("Press ENTER to start recording")
        print("Speak clearly and pause when done")
        print("(Say 'quit' to exit)")
        
        print("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1.0)
        
        recognizer.energy_threshold = 100
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 5.0  # After 5 seconds of silence, the recording stops
        recognizer.non_speaking_duration = 2.0
        
        try:
            print("🎤 Press ENTER to start recording...")
            input()  
            
            print("🟢 Recording... Speak now!")
            print("💡 The recording will stop when you pause speaking")
            
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=30)
            
            print("🔄 Processing speech...")
            text = recognizer.recognize_google(audio)
            
            print("\n📝 TRANSCRIPTION:")
            print("=" * 50)
            print(f"'{text}'")
            print("=" * 50)
            
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
            print(f"❌ Error type: {type(e).__name__}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
            return None
