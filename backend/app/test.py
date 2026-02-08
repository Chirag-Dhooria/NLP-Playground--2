import google.generativeai as genai

# --- PASTE YOUR ACTUAL API KEY HERE ---
KEY = "AIzaSyC73q7q7goAczr-1O3yy9WQTXaEdB8vvnU"

genai.configure(api_key=KEY)

print("Checking available models for your API key...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error: {e}")