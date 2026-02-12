from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
from textblob import TextBlob
from transformers import pipeline as hf_pipeline

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"

# Cache for heavy models (Singleton pattern recommended for production)
summarizer = None
qa_pipeline = None


def get_summarizer():
    global summarizer
    if summarizer is None:
        summarizer = hf_pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    return summarizer


def get_qa_pipeline():
    global qa_pipeline
    if qa_pipeline is None:
        qa_pipeline = hf_pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
    return qa_pipeline


def run_experiment(task_type: str, filename: str, input_col: str, target_col: str = None, context_col: str = None, hyperparameters: dict = {}):
    path = UPLOAD_DIR / filename
    df = pd.read_csv(path)

    if input_col and input_col in df.columns:
        df = df.dropna(subset=[input_col])

    if task_type == "classification":
        return _run_classification(df, input_col, target_col, hyperparameters)
    if task_type == "sentiment":
        return _run_sentiment(df, input_col)
    if task_type == "summarization":
        return _run_summarization(df, input_col)
    if task_type == "qa":
        return _run_qa(df, input_col, context_col)
    raise ValueError("Unknown Task")


def _run_classification(df, input_col, target_col, params):
    X = df[input_col]
    y = df[target_col]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    if params.get("model") == "RandomForest":
        clf = RandomForestClassifier(n_estimators=params.get("n_estimators", 100))
    else:
        clf = LogisticRegression(C=float(params.get("C", 1.0)))

    model = Pipeline([("tfidf", TfidfVectorizer()), ("clf", clf)])
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    report = classification_report(y_test, predictions, output_dict=True)
    return {"metrics": report, "type": "classification_metrics"}


def _run_sentiment(df, input_col):
    df["sentiment_score"] = df[input_col].apply(lambda x: TextBlob(str(x)).sentiment.polarity)
    df["sentiment_label"] = df["sentiment_score"].apply(
        lambda x: "positive" if x > 0 else ("negative" if x < 0 else "neutral")
    )

    distribution = df["sentiment_label"].value_counts().to_dict()
    return {
        "results": distribution,
        "type": "sentiment_analysis",
        "preview": df[[input_col, "sentiment_label"]].head(5).to_dict(),
    }


def _run_summarization(df, input_col):
    pipe = get_summarizer()
    sample = df[input_col].astype(str).head(5).tolist()
    summaries = pipe(sample, max_length=50, min_length=20, do_sample=False)
    return {"summaries": summaries, "type": "text_output"}


def _run_qa(df, question_col, context_col):
    pipe = get_qa_pipeline()
    results = []
    for _, row in df.head(5).iterrows():
        answer = pipe(question=row[question_col], context=row[context_col])
        results.append({"question": row[question_col], "answer": answer["answer"], "score": answer["score"]})
    return {"qa_results": results, "type": "text_output"}
