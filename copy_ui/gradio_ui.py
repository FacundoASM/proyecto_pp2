# ui/gradio_ui.py
import gradio as gr, requests, textwrap, html

API_URL = "http://localhost:8000/ask"

# ──────────────────────────────────────────────────────────────────────────────
def _abrev(txt: str, n: int = 60) -> str:
    """Acorta texto largo y escapa html para Markdown."""
    txt = html.escape(txt)
    return txt if len(txt) <= n else txt[:n] + "…"

def consultar_backend(pregunta: str):
    # Validación rápida
    if not pregunta.strip():
        return "⚠️ Escribe una consulta."

    yield "⏳ Procesando, por favor espera…"

    try:
        r = requests.get(API_URL, params={"question": pregunta}, timeout=60).json()

        # 1) Respuesta “conversacional” del modelo
        respuesta_md = textwrap.fill(r.get("respuesta", ""), width=90)

        # 2) Productos sugeridos en tabla Markdown
        prods = r.get("productos", [])
        if not prods:
            productos_md = "_Sin coincidencias._"
        else:
            header = (
                "| Tipo | Familia | Modelo | Descripción | Dimensiones | Potencia (W) | "
                "Litros | Máx P (bar) |\n"
                "|------|---------|--------|-------------|-------------|--------------|--------|------------|"
            )
            filas = "\n".join(
                f"| {p['type']} | {p['family']} | {p['model']} | {_abrev(p['description'])} | "
                f"{p['dimentions']} | {p['power_w']} | {p['liters']} | {p['max_pressure_bar']} |"
                for p in prods
            )
            productos_md = f"{header}\n{filas}"

        final_md = f"### Respuesta\n{respuesta_md}\n\n### Productos sugeridos\n{productos_md}"
        yield final_md

    except Exception as e:
        yield f"❌ Error al consultar la API: {e}"

# ──────────────────────────────────────────────────────────────────────────────
demo = gr.Interface(
    fn=consultar_backend,
    inputs=gr.Textbox(label="Pregunta", placeholder="Ejemplo: ¿Que caldera tiene al menos 17000 W?"),
    outputs=gr.Markdown(),
    title="Asistente de Repuestos",
    description="Consulta nuestro catálogo técnico.",
    allow_flagging="never",
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
