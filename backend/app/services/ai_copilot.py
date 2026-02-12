import os
from pathlib import Path

import google.generativeai as genai
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"


def _get_model():
    if not API_KEY:
        raise ValueError("GEMINI_API_KEY is not set in the environment.")
    genai.configure(api_key=API_KEY)
    return genai.GenerativeModel(MODEL_NAME)


def analyze_metadata(filename: str):
    path = UPLOAD_DIR / filename
    df = pd.read_csv(path)
    metadata = {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "column_names": df.columns.tolist(),
        "missing_values": df.isnull().sum().to_dict(),
        "dtypes": {k: str(v) for k, v in df.dtypes.items()},
        "numerical_columns": df.select_dtypes(include=["number"]).columns.tolist(),
        "categorical_columns": df.select_dtypes(include=["object"]).columns.tolist(),
    }
    return metadata


async def consult_gemini(filename: str, user_query: str):
    try:
        model = _get_model()
        metadata = analyze_metadata(filename)

        prompt = f"""
        You are an expert Data Scientist acting as a consultant for an NLP Playground.

        Here is the metadata of the user's uploaded dataset:
        {metadata}

        The user is asking: "{user_query}"

        Answer concisely.
        """

        response = model.generate_content(prompt)
        return {"response": response.text, "metadata_context": metadata}

    except Exception as e:
        return {"response": f"**SYSTEM ERROR:** {str(e)}", "error": str(e)}
