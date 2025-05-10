"""
query.py – search the FAISS index and return top-k catalog items.

Uso:
    python query.py "¿Con qué puedo perforar un agujero de 8 mm en hormigón?" [-k 5]

Requisitos:
    pip install sentence-transformers faiss-cpu rich tabulate
    (y haber generado products.faiss + products.db con ingest.py)
"""

import sys, argparse, sqlite3, faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from rich import print
from rich.table import Table
from pathlib import Path

# MODEL_NAME = "sentence-transformers/distiluse-base-multilingual-cased-v2"
# INDEX_PATH = "products.faiss"
# DB_PATH    = "products.db"
# TOP_K_DEFAULT = 5

SCRIPT_DIR = Path(__file__).resolve().parent
DB_PATH    = SCRIPT_DIR.parent / "embeddings" / "products.db"
INDEX_PATH = SCRIPT_DIR.parent / "embeddings" / "products.faiss"
MODEL_NAME = "sentence-transformers/distiluse-base-multilingual-cased-v2"
TOP_K_DEFAULT = 10

def load_index(path: str):
    # return faiss.read_index(path)
    return faiss.read_index(str(path))

def embed(text: str, model) -> np.ndarray:
    vec = model.encode([text], normalize_embeddings=True)
    return vec.astype("float32")

def fetch_rows(conn, ids):
    placeholders = ",".join("?" * len(ids))
    q = f"SELECT rowid, sku, name, description, price FROM products WHERE rowid IN ({placeholders})"
    rows = conn.execute(q, ids).fetchall()
    return {row[0]: row[1:] for row in rows}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("question", help="Consulta en español del usuario")
    parser.add_argument("-k", "--top_k", type=int, default=TOP_K_DEFAULT,
                        help="Número de resultados")
    args = parser.parse_args()

    # Cargar recursos
    index = load_index(INDEX_PATH)
    model = SentenceTransformer(MODEL_NAME)
    conn  = sqlite3.connect(DB_PATH)

    # Embedding de la consulta
    q_emb = embed(args.question, model)
    D, I = index.search(q_emb, args.top_k)

    # Recuperar productos
    rows_map = fetch_rows(conn, [int(i)+1 for i in I[0]])  # rowid empieza en 1
    table = Table(title="Resultados Top-K")
    table.add_column("Rank")
    table.add_column("SKU", style="cyan")
    table.add_column("Nombre")
    table.add_column("Descripción")
    table.add_column("Precio")

    for rank, (idx, dist) in enumerate(zip(I[0], D[0]), 1):
        rowid = int(idx) + 1
        sku, name, desc = rows_map.get(rowid, ("?", "?", "?"))
        table.add_row(str(rank), sku, name, desc[:60] + ("…" if len(desc) > 60 else ""))

    print(table)

# --- API-friendly search function --------------------------------- #
def search(question: str, k: int = 10):
    """
    Devuelve una lista de dicts [{'sku':…, 'name':…, 'description':…}, …]
    con los k productos más similares a la consulta.
    """
    # Carga el índice y la BD sólo la primera vez (patrón singleton)
    global _INDEX, _MODEL, _CONN
    if "_INDEX" not in globals():
        _MODEL = SentenceTransformer(MODEL_NAME)
        _INDEX = load_index(str(INDEX_PATH))
        _CONN  = sqlite3.connect(str(DB_PATH))

    # Embedding de la pregunta
    vec = embed(question, _MODEL)
    D, I = _INDEX.search(vec, k)

    # Recuperar filas
    rows_map = fetch_rows(_CONN, [int(i)+1 for i in I[0]])
    resultados = []
    for idx in I[0]:
        rowid = int(idx) + 1
        sku, name, desc, price = rows_map.get(rowid, ("?", "?", "?", "?"))
        resultados.append({"sku": sku, "name": name, "description": desc, "price": price})
    return resultados

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python query.py \"<pregunta>\"")
        sys.exit(1)
    main()
