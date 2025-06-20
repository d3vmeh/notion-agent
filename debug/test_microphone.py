#!/usr/bin/env python3
"""
Microphone Test Script for Notion Task Manager
Tests microphone functionality using sounddevice (better for macOS M1/M2)
"""

import sys
import os

# Add parent directory to path to import speech_tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from speech_tools import test_microphone, listen_for_speech_push_to_talk
    import sounddevice as sd
    import numpy as np
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you have installed the requirements:")
    print("   pip install -r requirements.txt")
    sys.exit(1)

def main():
    print("🎤 MICROPHONE TEST FOR NOTION TASK MANAGER")
    print("=" * 60)
    print("This script tests microphone functionality using sounddevice")
    print("(Better compatibility with macOS M1/M2 chips)")
    print("=" * 60)
    
    # Test 1: Basic microphone functionality
    print("\n🔍 TEST 1: Basic Microphone Test")
    print("-" * 40)
    
    if test_microphone():
        print("✅ Basic microphone test PASSED")
    else:
        print("❌ Basic microphone test FAILED")
        print("💡 Troubleshooting tips:")
        print("   • Check microphone permissions in System Preferences")
        print("   • Ensure microphone is not muted")
        print("   • Try a different microphone if available")
        return
    
    # Test 2: Speech recognition test
    print("\n🔍 TEST 2: Speech Recognition Test")
    print("-" * 40)
    print("This will test the actual speech recognition functionality")
    print("You'll be prompted to speak a test phrase")
    
    while True:
        choice = input("\nWould you like to test speech recognition? (y/n): ").lower().strip()
        
        if choice in ['y', 'yes']:
            print("\n🎤 Starting speech recognition test...")
            print("💡 Say something like 'Hello, this is a test'")
            
            result = listen_for_speech_push_to_talk()
            
            if result:
                print(f"✅ Speech recognition successful!")
                print(f"📝 Recognized: '{result}'")
                
                if 'quit' in result:
                    print("👋 Goodbye!")
                    break
            else:
                print("❌ Speech recognition failed")
                print("💡 Try speaking more clearly or checking your microphone")
        
        elif choice in ['n', 'no']:
            print("👋 Skipping speech recognition test")
            break
        
        else:
            print("❌ Please enter 'y' or 'n'")
    
    # Test 3: Device information
    print("\n🔍 TEST 3: Audio Device Information")
    print("-" * 40)
    
    try:
        devices = sd.query_devices()
        print(f"📱 Found {len(devices)} audio devices:")
        
        for i, device in enumerate(devices):
            # Handle devices that might not have all properties (common on Windows)
            name = device.get('name', 'Unknown')
            max_inputs = device.get('max_inputs', 0)
            max_outputs = device.get('max_outputs', 0)
            default_samplerate = device.get('default_samplerate', 'Unknown')
            
            print(f"  {i}: {name}")
            print(f"     Inputs: {max_inputs}, Outputs: {max_outputs}")
            print(f"     Default sample rate: {default_samplerate}")
            print()
        
        # Show default devices (with error handling)
        try:
            default_input = sd.query_devices(kind='input')
            print(f"🎤 Default input device: {default_input.get('name', 'Unknown')}")
        except Exception as e:
            print(f"🎤 Default input device: Could not determine ({e})")
        
        try:
            default_output = sd.query_devices(kind='output')
            print(f"🔊 Default output device: {default_output.get('name', 'Unknown')}")
        except Exception as e:
            print(f"🔊 Default output device: Could not determine ({e})")
        
    except Exception as e:
        print(f"❌ Error getting device information: {e}")
        print("💡 This is common on some Windows systems with certain audio drivers")
    
    print("\n🎉 MICROPHONE TEST COMPLETE!")
    print("=" * 60)
    print("💡 If all tests passed, your microphone should work with the Notion Task Manager")
    print("💡 If you encountered issues, check the troubleshooting tips above")

if __name__ == "__main__":
    main() 