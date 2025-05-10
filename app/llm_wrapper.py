# app/llm_wrapper.py
import requests, json

MODEL = "gemma3:1b"

# SYSTEM = ("Eres un experto ferretero. Responde en español, "
#           "menciona siempre el SKU del producto recomendado "
#           "y explica brevemente el porqué.")

SYSTEM = ("Eres un experto ferretero. Responde en español, ten en cuenta la pregunta y comparala con el producto recomendado, si no es relevante, menciona que no hay un producto que se pueda recomendar. En caso de que el producto sea relevante, menciona el producto y explica brevemente el porqué, no es necesario listar todos los productos, solo el o los que sean relevantes. Menciona el nombre del producto, el SKU y el precio (en pesos argentinos) de acuerdo a la lista de productos que se te proporciona.")

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