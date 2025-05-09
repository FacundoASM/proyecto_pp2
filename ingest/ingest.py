"""
ingest.py – create FAISS index + SQLite catalog from a CSV

Usage:
    python ingest.py products_mock.csv

Requirements:
    pip install sentence-transformers faiss-cpu pandas tqdm
"""

import sys, os, sqlite3, faiss
import pandas as pd
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from pathlib import Path


# MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"  # 384-dim
MODEL_NAME = "sentence-transformers/distiluse-base-multilingual-cased-v2"
# DB_PATH = "../embeddings/products.db"
# INDEX_PATH = "../embeddings/products.faiss"

SCRIPT_DIR = Path(__file__).resolve().parent
DB_PATH    = SCRIPT_DIR.parent / "embeddings" / "products.db"
INDEX_PATH = SCRIPT_DIR.parent / "embeddings" / "products.faiss"

def normalize_text(row):
    parts = [
        str(row.get("name_en") or row.get("name")),
        str(row.get("description_en") or row.get("description")),
        str(row.get("category", "")),
    ]
    return " ".join([p for p in parts if p and p != "nan"])

def build_sqlite(df, path=DB_PATH):
    if os.path.exists(path):
        os.remove(path)
    conn = sqlite3.connect(path)
    df.to_sql("products", conn, index=False)
    conn.close()

def build_faiss(embeddings, path=INDEX_PATH):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    faiss.normalize_L2(embeddings)
    index.add(embeddings)
    # faiss.write_index(index, path)
    faiss.write_index(index, str(path))

def main(csv_path):
    if not os.path.exists(csv_path):
        print(f"CSV {csv_path} not found")
        return

    print("Loading CSV...")
    df = pd.read_csv(csv_path)
    texts = [normalize_text(r) for _, r in df.iterrows()]

    print(f"Generating embeddings with {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=64)
    
    print("Saving SQLite database...")
    build_sqlite(df)

    print("Building FAISS index...")
    build_faiss(embeddings)

    print(f"Done! Saved {DB_PATH} and {INDEX_PATH}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ingest.py <csv_file>")
        sys.exit(1)
    main(sys.argv[1])
