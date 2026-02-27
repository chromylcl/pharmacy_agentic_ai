import sys
import os
from dotenv import load_dotenv

# 1. Path Fix: Ensures 'app' can be imported even if you run from different folders
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.orchestrator import Orchestrator
# Import the voice functions we created in voice.py
try:
    from app.agents.voice import record_audio, transcribe_fuzzy_voice
except ImportError:
    print("⚠️  Warning: voice.py not found. Voice mode will be disabled.")

def main():
    # 2. Load API keys from .env
    load_dotenv()

    # 3. Initialize the Multi-Agent System
    try:
        agent_system = Orchestrator()
    except Exception as e:
        print(f"❌ Failed to initialize agents: {e}")
        return

    print("\n=== 💊 AGENTIC AI PHARMACY: MULTI-AGENT SYSTEM ===")
    print("System: Safety, Stock, Order, and Pharmacist Agents are Online.")
    print("--------------------------------------------------")

    while True:
        print("\nModes: [v] Voice | [t] Text | [exit]")
        mode = input("Select Mode: ").lower()

        if mode == 'exit':
            print("Shutting down...")
            break
        
        user_input = ""
        
        if mode == 'v':
            try:
                # Record from microphone and send to Groq Whisper
                audio_file = record_audio()
                user_input = transcribe_fuzzy_voice(audio_file)
                print(f"🎤 You said: \"{user_input}\"")
            except Exception as e:
                print(f"❌ Voice Error: {e}")
                continue
        elif mode == 't':
            user_input = input("Patient (Text): ")
        else:
            print("Invalid selection. Please use 'v', 't', or 'exit'.")
            continue

        if user_input.strip():
            try:
                # 4. Pass the 'fuzzy' input to the Orchestrator
                # The PharmacistAgent will handle the cleaning and extraction
                response = agent_system.handle(user_input)
                print(f"\n✅ System Outcome: {response}")
            except Exception as e:
                print(f"\n⚠️ [Agent Execution Error]: {e}")
            
            print("\n" + "-"*40)

if __name__ == "__main__":
    main()