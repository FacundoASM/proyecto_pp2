# app/main.py
from fastapi import FastAPI, Query
from query import query  # ajusta import según tu módulo
from app.llm_wrapper import answer

app = FastAPI()

@app.get("/ask")
def ask(question: str = Query(..., min_length=5)):
    top_items = query.search(question, k=5)
    respuesta = answer(question, top_items)
    # return {"respuesta": respuesta, "productos": top_items}
    return {"respuesta": respuesta}