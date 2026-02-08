from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from schemas import PreprocessRequest, TrainRequest, ChatRequest, RagQueryRequest
from services import data_processor, model_engine, ai_copilot, rag_engine

app = FastAPI(title="NLP Playground API", version="2.0.0")

# CORS for React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Vite default
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_location = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
    
    # Immediately analyze metadata for WPR 4 Copilot
    metadata = ai_copilot.analyze_metadata(file.filename)
    return {"filename": file.filename, "metadata": metadata}

@app.post("/preprocess")
def preprocess_data(request: PreprocessRequest):
    return data_processor.preprocess_text(request.filename, request.text_column, request.options)

@app.post("/train")
def train_model(request: TrainRequest):
    try:
        return model_engine.run_experiment(
            task_type=request.task_type,
            filename=request.filename,
            input_col=request.input_column,
            target_col=request.target_column,
            context_col=request.context_column,
            hyperparameters=request.hyperparameters
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/copilot/consult")
async def consult_copilot(request: ChatRequest):
    return await ai_copilot.consult_gemini(request.filename, request.user_query)

@app.post("/rag/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        file_location = f"{UPLOAD_DIR}/{file.filename}"
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)
        return rag_engine.index_document(file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rag/query")
async def query_document(request: RagQueryRequest):
    try:
        return rag_engine.query_document(request.filename, request.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
