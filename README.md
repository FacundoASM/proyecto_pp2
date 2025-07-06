
# proyecto_pp2

Consulta de repuestos a través de PLN

## Features

* TODO: Describe the key features of this project.
* Manages environment and dependencies using `requirements.txt` (add dependencies manually).
* Includes basic setup for Docker containerization.
* Includes placeholder structure for data processing, feature engineering, model training, and prediction API.
* Includes `.github/CODEOWNERS` file.
* No testing framework or CI/CD pipeline included by default.

## Project Structure

```
├── .github/            <- GitHub related files (e.g., CODEOWNERS)
├── .gitignore          <- Files ignored by Git
├── .dockerignore       <- Files ignored by Docker build context
├── .clinerules         <- Cline rules file (user-specific)
├── Dockerfile          <- Docker configuration for the project
├── LICENSE             <- Project license (MIT)
├── Makefile            <- (Optional) Shortcuts for common commands
├── README.md           <- This file
├── configs/            <- Configuration files (e.g., params.yaml)
├── data/               <- Project data (raw, processed)
│   ├── processed/
│   └── raw/
├── memory-bank/        <- User-specific memory bank directory
├── notebooks/          <- Jupyter notebooks for exploration
├── outputs/            <- Generated outputs (figures, reports, etc.)
├── requirements.txt    <- Project dependencies (initially commented out)
└── src/proyecto_pp2/ <- Source code package
    ├── __init__.py
    ├── data/           <- Data processing scripts
    ├── features/       <- Feature engineering scripts
    ├── models/         <- Model training and prediction scripts
    └── api/            <- API related code (e.g., FastAPI)
```

## Getting Started

### Prerequisites

* Python 3.12
* [Docker](https://docs.docker.com/get-docker/) (Optional, for containerized environment)
* Git

### Installation

1.  Clone the repository:
    ```bash
    git clone <repository-url>
    cd proyecto_pp2
    ```

2.  Create a virtual environment (recommended):
    ```bash
    python3.1 -m venv .venv # Or use uv, conda, etc.
    source .venv/bin/activate # On Windows use `.venv\Scripts\activate`
    ```

3.  **Add your project dependencies** to `requirements.txt`.

4.  Install dependencies:
    ```bash
    pip install -r requirements.txt # Or use uv pip install -r requirements.txt
    ```
    *(Consider creating a `requirements-dev.txt` for tools like jupyterlab and installing with `pip install -r requirements-dev.txt`)*

### Using Docker (Alternative)

1.  **Add dependencies** to `requirements.txt`.
2.  Build the Docker image:
    ```bash
    docker build -t proyecto_pp2 .
    ```
3.  Run a container (example: interactive shell):
    ```bash
    docker run -it --rm -v "${PWD}":/app proyecto_pp2 bash
    ```
    *(Note: Adjust volume mounts and ports as needed)*

## Usage

* **Data Processing:** `python src/proyecto_pp2/data/make_dataset.py` (Modify as needed)
* **Training:** `python src/proyecto_pp2/models/train_model.py` (Modify as needed)
* **API (if applicable):** `uvicorn src.proyecto_pp2.api.main:app --reload` (Modify as needed, requires `fastapi` and `uvicorn` in `requirements.txt`)

(Consider adding details on how to run commands via `Makefile` if you include one)

## Contributing

TODO: Add contribution guidelines if applicable.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 Equipo Soldasur PP2.

---

# Resumen Ejecutivo – Proyecto “Asistente de Repuestos con IA”

| Aspecto | Descripción breve |
|---------|------------------|
| **Objetivo** | Responder en lenguaje natural (texto/voz) a preguntas técnicas de clientes y sugerir, a partir de su catálogo, los productos adecuados (tornillos, tarugos, abrasivos, etc.). |
| **Plazo** | 14 días (un sprint). |
| **Éxito** | ✅ MVP que corre en una notebook, ingiere un CSV real, busca de forma semántica y devuelve la respuesta razonada en la web. |

---

## 1. Entregables

1. **Motor RAG local** (embeddings + LLM).  
2. **API** REST (`/ask`, `/upload‑csv`) con documentación OpenAPI.  
3. **UI web** minimalista (Gradio) con voz opcional.  
4. **Script de ingesta** para subir/actualizar catálogos (CSV→SQLite→FAISS).  
5. **Docker compose** para levantar todo con un único comando.  
6. **Manual + vídeo demo** (< 5 min) y checklist de pruebas.

---

## 2. Arquitectura en tres capas

```text
[ UI Web (Gradio) ]
         │ HTTP
         ▼
[ FastAPI RAG Service ]──► [ FAISS (+SQLite) ]   ← embeddings
         │
         └──► [ Llama‑3‑8B‑Instruct (Ollama) ]   ← prompt + contexto
```

---

## 3. Pila tecnológica

| Dominio          | Herramientas                                            |
| ---------------- | ------------------------------------------------------- |
| Embeddings       | `sentence-transformers` (MiniLM-L6-v2)                  |
| Vector store     | **FAISS**                                               |
| LLM              | **Llama-3-8B-Instruct** vía **Ollama**                  |
| API              | **FastAPI** + `langchain`                               |
| Frontend         | **Gradio** (+ Tailwind & htmx para + UX)                |
| STT/TTS opcional | `whisper-cpp` · Web Speech API                          |
| Datos            | **SQLite** (persistencia)                               |
| DevOps           | Docker + docker-compose, GitHub, Trello, pytest, locust |

---

## 4. Cronograma agil

| Día | Meta                           | Quien lidera\* |
| --- | ------------------------------ | -------------- |
| 1   | Kick-off, backlog, FigJam      | Ambos          |
| 2   | Diseño datos (+ plantilla CSV) | Tú             |
| 3   | Ingesta & embeddings           | Yo             |
| 4   | Búsqueda semántica + tests     | Yo             |
| 5   | Prompt + Llama-3               | Yo             |
| 6   | API REST básica                | Yo             |
| 7   | UI Gradio MVP                  | Tú             |
| 8   | STT (Whisper)                  | Yo             |
| 9   | TTS (SpeechSynthesis)          | Tú             |
| 10  | UX polishing (Tailwind)        | Tú             |
| 11  | Seguridad, validación          | Yo             |
| 12  | Docker & compose               | Yo             |
| 13  | QA, carga, fixes               | Ambos          |
| 14  | Handoff, demo, docs            | Ambos          |

---

## 5. Flujo de desarrollo
Repositorio Git (branch main + feature branches).

    1. Trello: listas Product Backlog → Sprint Backlog → To Do → Doing → Done.

    2. Daily async (mensaje breve en el Trello card de “Sprint Backlog”).

    3. PR + Code review: checklist de lint, tests y cobertura.

---

## 6. Requisitos previos
- **Python ≥ 3.11**, GPU opcional (CPU vale con cuantización 4-bit).

- **Docker ≥ 24**, Docker Compose v2.

- **16 GB RAM recomendado**; 10 GB disco libres.

- **CSV inicial con columnas mínimas**: sku, nombre, descripcion, categoria, stock, precio.

---

## 7. Gestión de riesgos

| Riesgo                         | Plan B                                                         |
| ------------------------------ | -------------------------------------------------------------- |
| Llama-3 mediático en CPU lento | Cuantizar (Q4\_K\_M) o cambiar a Phi-3-mini (faster).          |
| CSV con formatos incoherentes  | Validación pydantic + plantilla ejemplo.                       |
| Escalabilidad catálogo > 100 k | Migrar de FAISS local a Qdrant Cloud (misma API de LangChain). |
| Tiempo de respuesta alto       | Cache de embeddings y respuestas frecuentes.                   |

## 8. Lanzar la aplicación

```cmd
uvicorn app.main:app --reload
```