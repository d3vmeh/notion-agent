import speech_recognition as sr

def test_microphone():
    """Simple microphone test to check if audio input is working"""
    print("🎤 MICROPHONE TEST")
    print("=" * 50)
    
    # Test 1: Check if microphone is available
    try:
        mic = sr.Microphone()
        print("✅ Microphone found and accessible")
    except Exception as e:
        print(f"❌ Microphone error: {e}")
        return False
    
    # Test 2: List available microphones
    try:
        print("\n📋 Available microphones:")
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            print(f"  {index}: {name}")
    except Exception as e:
        print(f"❌ Could not list microphones: {e}")
    
    # Test 3: Try to access microphone
    try:
        with mic as source:
            print(f"\n🎙️  Using microphone: {source.device_index}")
            
            # Test 4: Adjust for ambient noise
            print("🔧 Adjusting for ambient noise...")
            recognizer = sr.Recognizer()
            recognizer.adjust_for_ambient_noise(source, duration=2.0)
            print("✅ Ambient noise adjustment complete")
            
            # Test 5: Try to record audio
            print("\n🎤 Testing audio recording...")
            print("💡 Speak something for 5 seconds...")
            
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                print("✅ Audio recorded successfully!")
                
                # Test 6: Try to recognize speech
                print("🔄 Attempting speech recognition...")
                text = recognizer.recognize_google(audio)
                print(f"✅ Speech recognized: '{text}'")
                
                return True
                
            except sr.WaitTimeoutError:
                print("❌ No speech detected within 5 seconds")
                return False
            except sr.UnknownValueError:
                print("❌ Speech was recorded but could not be understood")
                return False
            except sr.RequestError as e:
                print(f"❌ Speech recognition service error: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Error accessing microphone: {e}")
        return False

def test_simple_recording():
    """Even simpler test - just try to record without recognition"""
    print("\n🎤 SIMPLE RECORDING TEST")
    print("=" * 50)
    
    try:
        recognizer = sr.Recognizer()
        
        with sr.Microphone() as source:
            print("🎙️  Microphone opened successfully")
            
            # Set very sensitive settings
            recognizer.energy_threshold = 50
            recognizer.dynamic_energy_threshold = False
            recognizer.pause_threshold = 0.5
            
            print("🔧 Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1.0)
            
            print("🎤 Speak something now (5 seconds)...")
            print("💡 Make sure your microphone is not muted!")
            
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                print("✅ Audio captured successfully!")
                print(f"📊 Audio length: {len(audio.frame_data)} bytes")
                return True
                
            except sr.WaitTimeoutError:
                print("❌ No audio detected - microphone might be muted or not working")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Starting microphone tests...\n")
    
    # Run comprehensive test
    print("TEST 1: Comprehensive Microphone Test")
    result1 = test_microphone()
    
    print("\n" + "="*50 + "\n")
    
    # Run simple test
    print("TEST 2: Simple Recording Test")
    result2 = test_simple_recording()
    
    print("\n" + "="*50)
    print("SUMMARY:")
    print(f"Comprehensive test: {'✅ PASSED' if result1 else '❌ FAILED'}")
    print(f"Simple recording test: {'✅ PASSED' if result2 else '❌ FAILED'}")
    
    if not result1 and not result2:
        print("\n🔧 TROUBLESHOOTING TIPS:")
        print("1. Check if your microphone is muted")
        print("2. Check Windows microphone permissions")
        print("3. Try a different microphone if available")
        print("4. Restart your computer")
        print("5. Check if other apps can use your microphone")
    
    input("\nPress ENTER to exit...") 