import speech_recognition as sr
import threading
import time
import keyboard
import queue


def listen_for_speech():
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("🎤 Listening... Speak your task now!")
        print("(Say 'quit' to exit)")
        
    
        print("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1.0)
        

        recognizer.energy_threshold = 300  
        recognizer.dynamic_energy_threshold = True  
        recognizer.pause_threshold = 0.8  
        
        try:
            print("🎤 Start speaking...")
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
            print("Processing speech...")
            
            text = recognizer.recognize_google(audio)
            print(f"You said: '{text}'")
            return text.lower()
            
        except sr.WaitTimeoutError:
            print("No speech detected within 10 seconds. Please try again.")
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


def listen_for_speech_continuous():
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("🎤 Continuous listening mode...")
        print("Speak your task and pause when done (or say 'quit' to exit)")
        
        recognizer.adjust_for_ambient_noise(source, duration=1.0)
        
 
        recognizer.energy_threshold = 250
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 1.2  
        
        try:
            print("🎤 Start speaking...")
            audio = recognizer.listen(source, timeout=15, phrase_time_limit=20)
            print("Processing speech...")
            
            text = recognizer.recognize_google(audio)
            print(f"You said: '{text}'")
            return text.lower()
            
        except sr.WaitTimeoutError:
            print("No speech detected within 15 seconds. Please try again.")
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


def listen_for_speech_push_to_talk():
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("🎤 Push-to-Talk Mode")
        print("Press and HOLD SPACE to talk, release to stop")
        print("(Say 'quit' to exit)")
        

        print("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1.0)
        
        recognizer.energy_threshold = 200
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 0.5 
        
        try:
            print("🎤 Press and HOLD SPACE to talk...")
            audio = recognizer.listen(source, timeout=30, phrase_time_limit=30)
            print("Processing speech...")
            
            text = recognizer.recognize_google(audio)
            print(f"You said: '{text}'")
            return text.lower()
            
        except sr.WaitTimeoutError:
            print("No speech detected. Press and hold SPACE to try again.")
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


def listen_for_speech_push_to_talk_advanced():
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("🎤 Advanced Push-to-Talk Mode")
        print("Press and HOLD SPACE to talk, release to stop")
        print("(Say 'quit' to exit)")
        
        recognizer.adjust_for_ambient_noise(source, duration=1.0)
        
        recognizer.energy_threshold = 150
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 0.3  
        
        try:
            print("🎤 Press and HOLD SPACE to talk...")
            print("🔴 Waiting for SPACE key...")
            
            # Wait for space key press
            input("Press ENTER when ready to start listening...")
            print("🟢 Listening... (Press ENTER again to stop)")
            
            audio = recognizer.listen(source, timeout=60, phrase_time_limit=60)
            print("🔄 Processing speech...")
            
            # Use Google's speech recognition
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


def listen_for_speech_true_push_to_talk():
    """True push-to-talk: Hold SPACE key to record, release to stop"""
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("🎤 Push-to-Talk Mode")
        print("HOLD DOWN the SPACE key while talking")
        print("RELEASE SPACE when done")
        print("(Say 'quit' to exit)")
        
        print("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1.0)
        
        recognizer.energy_threshold = 100 
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 0.1 
        
        try:
            print("🎤 HOLD SPACE and start talking...")
            
            audio_queue = queue.Queue()
            recording_stopped = threading.Event()
            
            def record_audio():
                """Record audio in a separate thread"""
                try:
                    with sr.Microphone() as mic_source:
                        audio = recognizer.listen(mic_source, timeout=60, phrase_time_limit=60)
                        audio_queue.put(audio)
                except Exception as e:
                    audio_queue.put(e)
            
            def check_space_key():
                """Monitor space key in a separate thread"""
                while not recording_stopped.is_set():
                    if not keyboard.is_pressed('space'):
                        recording_stopped.set()
                        break
                    time.sleep(0.1)
            
            record_thread = threading.Thread(target=record_audio)
            record_thread.daemon = True
            record_thread.start()
            
            space_thread = threading.Thread(target=check_space_key)
            space_thread.daemon = True
            space_thread.start()
            
            print("🟢 Recording... (Release SPACE to stop)")
            
            while not recording_stopped.is_set() and record_thread.is_alive():
                time.sleep(0.1)
            
            recording_stopped.set()
            
            try:
                audio = audio_queue.get(timeout=1)
                if isinstance(audio, Exception):
                    raise audio
                
                print("🔄 Processing speech...")
                text = recognizer.recognize_google(audio)
                print(f"✅ You said: '{text}'")
                return text.lower()
                
            except queue.Empty:
                print("❌ No audio recorded. Try again.")
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


def listen_for_speech_simple_push_to_talk():
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("🎤 Push-to-Talk Mode")
        print("Press ENTER to start recording")
        print("Press ENTER again to stop recording")
        print("(Say 'quit' to exit)")
        
        print("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1.0)
        
        # Optimized settings
        recognizer.energy_threshold = 150
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 0.2
        
        try:
            print("🎤 Press ENTER to start recording...")
            
            print("🟢 Recording... Press ENTER to stop")
            
            # Start recording in a separate thread
            audio_queue = queue.Queue()
            recording_stopped = threading.Event()
            
            def record_audio():
                try:
                    with sr.Microphone() as mic_source:
                        audio = recognizer.listen(mic_source, timeout=60, phrase_time_limit=60)
                        if not recording_stopped.is_set():
                            audio_queue.put(audio)
                except Exception as e:
                    if not recording_stopped.is_set():
                        audio_queue.put(e)
            
            record_thread = threading.Thread(target=record_audio)
            record_thread.daemon = True
            record_thread.start()
            
            input("Press ENTER to stop recording...")
            recording_stopped.set()
            
            try:
                audio = audio_queue.get(timeout=2)
                if isinstance(audio, Exception):
                    raise audio
                
                print("🔄 Processing speech...")
                text = recognizer.recognize_google(audio)
                print(f"✅ You said: '{text}'")
                return text.lower()
                
            except queue.Empty:
                print("❌ No audio recorded. Try again.")
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
