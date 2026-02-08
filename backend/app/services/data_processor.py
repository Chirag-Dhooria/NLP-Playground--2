import pandas as pd
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk.tokenize import word_tokenize
import os

# Ensure resources are downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('punkt_tab')

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def load_data(filename: str) -> pd.DataFrame:
    """Securely loads data from the upload directory."""
    path = os.path.join(UPLOAD_DIR, filename)
    if filename.endswith('.csv'):
        return pd.read_csv(path)
    elif filename.endswith('.json'):
        return pd.read_json(path)
    raise ValueError("Unsupported file format")

def preprocess_text(filename: str, text_column: str, options: dict) -> dict:
    df = load_data(filename)
    
    # Your Original Logic Preserved
    df['processed_text'] = df[text_column].astype(str)
    if options.get('lowercase', False):
        df['processed_text'] = df['processed_text'].apply(lambda x: x.lower())
    if options.get('remove_punctuation', False):
        df['processed_text'] = df['processed_text'].apply(lambda x: x.translate(str.maketrans('', '', string.punctuation)))
    if options.get('remove_stopwords', False):
        stop_words = set(stopwords.words('english'))
        df['processed_text'] = df['processed_text'].apply(lambda x: " ".join([word for word in x.split() if word.lower() not in stop_words]))
    if options.get('lemmatization', False):
        lemmatizer = WordNetLemmatizer()
        df['processed_text'] = df['processed_text'].apply(lambda x: " ".join([lemmatizer.lemmatize(word) for word in word_tokenize(x)]))
    elif options.get('stemming', False): 
        stemmer = PorterStemmer()
        df['processed_text'] = df['processed_text'].apply(lambda x: " ".join([stemmer.stem(word) for word in word_tokenize(x)]))
    
    # Save intermediate state for next steps
    df.to_csv(os.path.join(UPLOAD_DIR, filename), index=False)
    
    return {"message": "Preprocessing complete", "preview": df[['processed_text']].head().to_dict(orient='records')}