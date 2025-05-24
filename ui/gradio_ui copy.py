# import textwrap, requests, gradio as gr
import gradio as gr, requests, textwrap, time


API_URL = "http://localhost:8000/ask"

def consultar_backend(pregunta):
    if not pregunta.strip():
        return "⚠️ Escribe una consulta."

    placeholder = "⏳ Procesando, por favor espera…"
    yield placeholder                 # Gradio actualiza de inmediato

    try:
        r = requests.get(API_URL, params={"question": pregunta}, timeout=60).json()
        productos = "\n".join(
            f"- **{p['sku']}** | {p['name']} | ${p['price']}"
            for p in r.get("productos", [])
        )
        respuesta = textwrap.fill(r.get("respuesta", str(r)), width=90)
        final_text = f"### Respuesta\n{respuesta}\n\n### Productos sugeridos\n{productos}"
        yield final_text              # segundo update: respuesta real
    except Exception as e:
        yield f"❌ Error al consultar la API: {e}"

demo = gr.Interface(
    fn=consultar_backend,
    inputs=gr.Textbox(label="Pregunta", placeholder="¿Qué tarugos uso para…?"),
    outputs=gr.Markdown(),
    title="Asistente de Repuestos",
    description="Consulta sobre nuestros productos.",
    allow_flagging="never"      # 👈 oculta el botón “Flag”

)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
