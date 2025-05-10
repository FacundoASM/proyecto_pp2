# ui/gradio_ui.py
import gradio as gr, requests

def ask_api(q):
    r = requests.get("http://localhost:8000/ask", params={"question": q}).json()
    return r["respuesta"]

demo = gr.Interface(fn=ask_api, inputs=gr.Textbox(label="Pregunta"), outputs="text")
demo.launch()
