import speech_recognition as sr
import sounddevice as sd


def listen_for_speech_push_to_talk():

    recognizer = sr.Recognizer()
    
    # Configure for better performance
    recognizer.energy_threshold = 100
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 5.0  # After 5 seconds of silence, the recording stops
    recognizer.non_speaking_duration = 2.0
    
    # Show which device is being used
    try:
        current_device = sd.query_devices(kind='input')
        print(f"🎤 Using input device: {current_device.get('name', 'Unknown')}")
    except Exception as e:
        print(f"🎤 Input device: Could not determine ({e})")
    
    print("🎤 Push-to-Talk Mode (sounddevice backend)")
    print("Press ENTER to start recording")
    print("Speak clearly and pause when done")
    print("(Say 'quit' to exit)")
    
    try:
        print("🎤 Press ENTER to start recording...")
        input()
        
        print("🟢 Recording... Speak now!")
        print("💡 The recording will stop when you pause speaking")
        
        # Use sounddevice to record audio
        sample_rate = 16000
        channels = 1
        
        # Record audio using sounddevice
        audio_data = sd.rec(int(sample_rate * 30), samplerate=sample_rate, channels=channels, dtype='int16')
        sd.wait()  # Wait until recording is finished
        
        # Convert to speech_recognition AudioData format
        audio = sr.AudioData(audio_data.tobytes(), sample_rate, 2)
        
        print("🔄 Processing speech...")
        text = recognizer.recognize_google(audio)
        
        print("\n📝 TRANSCRIPTION:")
        print("=" * 50)
        print(f"'{text}'")
        print("=" * 50)
        
        return text.lower()
        
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

def listen_for_speech_continuous():
    """
    Continuous speech recognition with sounddevice
    Automatically detects speech and stops when silence is detected
    """
    recognizer = sr.Recognizer()
    
    # Configure for continuous listening
    recognizer.energy_threshold = 100
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 3.0
    recognizer.non_speaking_duration = 1.0
    
    # Show which device is being used
    try:
        current_device = sd.query_devices(kind='input')
        print(f"🎤 Using input device: {current_device.get('name', 'Unknown')}")
    except Exception as e:
        print(f"🎤 Input device: Could not determine ({e})")
    
    print("🎤 Continuous Listening Mode (sounddevice backend)")
    print("Speak naturally - recording will stop automatically")
    print("(Say 'quit' to exit)")
    
    try:
        print("🟢 Listening... Speak now!")
        
        # Use sounddevice for continuous recording
        sample_rate = 16000
        channels = 1
        
        # Record with automatic silence detection
        audio_data = sd.rec(int(sample_rate * 60), samplerate=sample_rate, channels=channels, dtype='int16')
        sd.wait()
        
        # Convert to speech_recognition AudioData format
        audio = sr.AudioData(audio_data.tobytes(), sample_rate, 2)
        
        print("🔄 Processing speech...")
        text = recognizer.recognize_google(audio)
        
        print("\n📝 TRANSCRIPTION:")
        print("=" * 50)
        print(f"'{text}'")
        print("=" * 50)
        
        return text.lower()
        
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

def test_microphone():
    """
    Test microphone functionality with sounddevice
    Cross-platform compatible for Windows, macOS, and Linux
    """
    print("🎤 Testing microphone with sounddevice...")
    
    try:
        # List available devices
        devices = sd.query_devices()
        print(f"📱 Found {len(devices)} audio devices:")
        
        for i, device in enumerate(devices):
            # Handle devices that might not have all properties
            name = device.get('name', 'Unknown')
            max_inputs = device.get('max_inputs', 0)
            max_outputs = device.get('max_outputs', 0)
            
            print(f"  {i}: {name} (inputs: {max_inputs}, outputs: {max_outputs})")
        
        # Test recording
        print("\n🎤 Testing recording (3 seconds)...")
        sample_rate = 16000
        audio_data = sd.rec(int(sample_rate * 3), samplerate=sample_rate, channels=1, dtype='int16')
        sd.wait()
        
        print("✅ Recording test successful!")
        print(f"📊 Recorded {len(audio_data)} samples at {sample_rate}Hz")
        
        return True
        
    except Exception as e:
        print(f"❌ Microphone test failed: {e}")
        print("💡 This might be a permission issue or device configuration problem")
        return False
