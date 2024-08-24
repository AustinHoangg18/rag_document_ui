from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
import requests
import PyPDF2
import json
from backend.rag import *
from typing import Dict


app = FastAPI()

qa_storage: Dict[str, object] = {}

@app.post('/fetch')
async def read_file(file: UploadFile = File(...)):
    pdf_reader = PyPDF2.PdfReader(file.file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()

    documents = [Document(page_content=doc) for doc in split_text(text)]
    qa = setup_chain(documents)
    qa_storage['qa'] = qa
    return {"message":"File read complete!!!"}

@app.post('/chat/{question}')
async def chat_response(question: str):
    print(question)
    qa = qa_storage.get('qa')
    response = qa.invoke(question)
    print(response)
    return {"message": response['result']}



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8003,debug=True)