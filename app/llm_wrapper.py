# app/llm_wrapper.py
import requests, json

MODEL = "gemma2:2b"

SYSTEM = ("Eres un técnico experto en equipos de calefacción. Tu tarea es responder preguntas basándote en productos de: Catálogo relevante")


def answer(question: str, context: list[dict]) -> str:
    prompt = SYSTEM + "\n\n" \
        "Catálogo relevante:\n" + \
        "\n".join(f"- {p['type']}: {p['family']} — {p['model']} — {p['description']} — {p['dimentions']} - {p['power_w']} - {p['liters']} - {p['max_pressure_bar']}"
                  for p in context) + \
        f"\n\nPregunta: {question}\nRespuesta:"

    resp = requests.post(
    "http://localhost:11434/api/generate",
    json={"model": MODEL, "prompt": prompt, "stream": False},
    timeout=180
    ).json()

    print("DEBUG Ollama:", resp)   #  ← añade esta línea

    if "response" not in resp:
        raise ValueError(resp.get("error", "Respuesta inesperada de Ollama"))

    return resp["response"].strip()