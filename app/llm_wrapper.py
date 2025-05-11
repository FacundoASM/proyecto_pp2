# app/llm_wrapper.py
import requests, json

MODEL = "gemma2:2b"

# SYSTEM = ("Eres un experto ferretero. Responde en español, "
#           "menciona siempre el SKU del producto recomendado "
#           "y explica brevemente el porqué.")

SYSTEM = ("""
Eres un experto ferretero experto. Instrucciones:
1. Lee SOLO la lista “Catálogo relevante”.
2. Si encuentras al menos 1 producto que resuelva la pregunta, cítalos copiando SKU, nombre y precio exactamente como aparecen.
3. Explica brevemente (máx. 3 frases) por qué son adecuados.
4. Si ninguno sirve, responde: «No hay producto recomendable en el catálogo.
5. Responde SIEMPRE en español claro, técnico y con un tono amigable.
""")


def answer(question: str, context: list[dict]) -> str:
    prompt = SYSTEM + "\n\n" \
        "Catálogo relevante:\n" + \
        "\n".join(f"- {p['sku']}: {p['name']} — {p['description']} — {p['price']}"
                  for p in context) + \
        f"\n\nPregunta: {question}\nRespuesta:"

    resp = requests.post(
    "http://localhost:11434/api/generate",
    json={"model": MODEL, "prompt": prompt, "stream": False},
    timeout=60
    ).json()

    print("DEBUG Ollama:", resp)   #  ← añade esta línea

    if "response" not in resp:
        raise ValueError(resp.get("error", "Respuesta inesperada de Ollama"))

    return resp["response"].strip()