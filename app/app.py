from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
import math
from math import ceil
from bisect import bisect_left
from .models import RADIATOR_MODELS

knowledge_base = None

def init_knowledge_base(kb):
    """Inicializa la base de conocimiento"""
    global knowledge_base
    knowledge_base = kb

def get_node_by_id(node_id):
    """Busca un nodo por su ID en la base de conocimiento"""
    if knowledge_base is None:
        raise RuntimeError("Knowledge base not initialized")
    for node in knowledge_base:
        if node.get('id') == node_id:
            return node
    return None

def replace_variables(text: str, context: Dict[str, Any]) -> str:
    """Reemplaza variables en el texto usando el contexto"""
    if not isinstance(text, str):
        return text
        
    for key, val in context.items():
        if isinstance(val, (int, float, str)):
            text = text.replace("{{"+key+"}}", str(val))
    
    try:
        from jinja2 import Template
        template = Template(text)
        return template.render(**context)
    except Exception as e:
        print(f"Error en template Jinja2: {e}")
        return text

def filter_radiators(radiator_type: str, installation: str, style: str, color: str, heat_load: float) -> List[Dict[str, Any]]:
    """Filtra radiadores según las preferencias del usuario"""
    recommended = []
    
    for name, model in RADIATOR_MODELS.items():
        # Filtrar por tipo de radiador (aceptar si coincide o si está en la lista)
        if isinstance(model.get('type'), str):
            if model.get('type') != radiator_type:
                continue
        else:
            if radiator_type not in model.get('type', []):
                continue
                
        # Filtrar por tipo de instalación
        if installation != 'cualquiera':
            if isinstance(model['installation'], str):
                if model['installation'] != installation:
                    continue
            elif installation not in model['installation']:
                continue
                
        # Filtrar por estilo
        if style != 'cualquiera' and model['style'] != style:
            continue
            
        # Filtrar por color
        if color != 'cualquiera' and color not in model['colors']:
            continue
            
        recommended.append({
            'name': name,
            'description': model['description'],
            'coeficiente': model.get('coeficiente', 1.0),
            'potencia': model['potencia'],
            'colors': model['colors']
        })
    
    # Ordenar por mejor ajuste a la carga térmica
    recommended.sort(key=lambda x: abs(x['potencia'] * x['coeficiente'] - heat_load))
    
    return recommended[:3]  # Top 3 recomendaciones

def format_radiator_recommendations(models: List[Dict[str, Any]], heat_load: float) -> str:
    """Formatea las recomendaciones para mostrarlas al usuario"""
    if not models or not isinstance(models, list):
        return "No encontramos modelos que coincidan con tus requisitos. Por favor intenta con diferentes parámetros."
    
    result = []
    for i, model in enumerate(models, 1):
        try:
            potencia_efectiva = model.get('potencia', 0) * model.get('coeficiente', 1)
            modulos_estimados = ceil(heat_load / potencia_efectiva) if potencia_efectiva > 0 else 0
            
            model_info = [
                f"{i}. {model.get('name', 'Modelo desconocido')}",
                f"   - Potencia efectiva: {potencia_efectiva:.0f} kcal/h",
                f"   - Módulos estimados: {modulos_estimados}",
                f"   - Descripción: {model.get('description', 'Sin descripción disponible')}"
            ]
            
            if 'colors' in model:
                model_info.append(f"   - Colores disponibles: {', '.join(model['colors'])}")
                
            result.append("\n".join(model_info))
        except Exception as e:
            print(f"Error formateando modelo {model}: {e}")
            continue
    
    return "\n\n".join(result) if result else "No se pudieron generar recomendaciones."

def perform_calculation(node: Dict[str, Any], context: Dict[str, Any]) -> None:
    """Ejecuta los cálculos definidos en un nodo"""
    params = node.get("parametros", {})
    for key, val in params.items():
        context[key] = val

    for action in node.get("acciones", []):
        exec_expression(action, context)

def exec_expression(expr: str, context: Dict[str, Any]) -> None:
    """Ejecuta una expresión matemática y guarda el resultado en el contexto"""
    try:
        # Agregar funciones especiales al contexto
        local_context = {
            'filter_radiators': filter_radiators,
            'format_radiator_recommendations': format_radiator_recommendations,
            'ceil': ceil,
            'context': context  # Pasamos el contexto completo
        }
        
        # Dividir la expresión en variable y valor
        var, val_expr = [x.strip() for x in expr.split("=", 1)]
        
        # Reemplazar context['variable'] por simplemente variable
        val_expr = val_expr.replace("context['", "").replace("']", "")
        
        # Evaluar la expresión con las variables del contexto
        val = eval(val_expr, {"__builtins__": None}, {**context, **local_context})
        context[var] = val
    except Exception as e:
        print(f"Error evaluando expresión '{expr}': {e}")
        raise




