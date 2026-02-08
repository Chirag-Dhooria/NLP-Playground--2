import google.generativeai as genai
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

UPLOAD_DIR = "uploads"

def _get_model():
    if not API_KEY:
        raise ValueError("GEMINI_API_KEY is not set in the environment.")
    genai.configure(api_key=API_KEY)
    return genai.GenerativeModel(MODEL_NAME)

def analyze_metadata(filename: str):
    # Robust path finding
    base_dir = os.getcwd()
    # Check if we are already inside 'backend' or 'app'
    if "app" in base_dir:
        path = os.path.join(base_dir, "uploads", filename)
    else:
        path = os.path.join(base_dir, "backend", "app", "uploads", filename)

    print(f"DEBUG: Reading file from {path}") # <--- DEBUG PRINT
    
    try:
        df = pd.read_csv(path)
        metadata = {
            "rows": df.shape[0],
            "columns": df.shape[1],
            "column_names": df.columns.tolist(),
            "missing_values": df.isnull().sum().to_dict(),
            "dtypes": {k: str(v) for k, v in df.dtypes.items()},
            "numerical_columns": df.select_dtypes(include=['number']).columns.tolist(),
            "categorical_columns": df.select_dtypes(include=['object']).columns.tolist()
        }
        return metadata
    except Exception as e:
        print(f"METADATA ERROR: {str(e)}")
        raise e

async def consult_gemini(filename: str, user_query: str):
    try:
        model = _get_model()
        # 1. Get Metadata
        metadata = analyze_metadata(filename)
        
        # 2. Prove it exists by printing to Terminal
        print("\n--- DEBUG: METADATA SENT TO MODEL ---")
        print(metadata) 
        print("-------------------------------------\n")
        
        prompt = f"""
        You are an expert Data Scientist acting as a consultant for an NLP Playground.
        
        Here is the metadata of the user's uploaded dataset:
        {metadata}
        
        The user is asking: "{user_query}"
        
        Answer concisely.
        """
        
        # 3. Call the Model
        response = model.generate_content(prompt)
        return {"response": response.text, "metadata_context": metadata}

    except Exception as e:
        # 4. SHOW THE REAL ERROR
        print(f"\n!!! GEMINI CRASH !!!\nError: {str(e)}\n")
        # Return the ACTUAL error to the chat window so we can read it
        return {"response": f"**SYSTEM ERROR:** {str(e)}", "error": str(e)}
