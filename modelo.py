import numpy as np
import pandas as pd
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
import os
from dotenv import load_dotenv
import json

# CONFIGURACION INICIAL
load_dotenv(override=True)
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# CARGAR DATOS
def cargar_datos():
    df_nutricion = pd.read_csv("nutricion.csv")
    df_nutricion = df_nutricion.set_index("id")

    df_precios = pd.read_csv("recetas_precio.csv")
    df_precios = df_precios.set_index("id")

    with open("modelo.pkl", "rb") as f:
        df_modelo = pickle.load(f)
        df_modelo = df_modelo.reset_index(drop=True)

    # MERGE
    df = df_modelo.merge(df_precios, on="id")
    df = df.merge(df_nutricion, on="id")

    return df

def aplicar_filtros(df, vegano, vegetariano, precio_max, tiempo_max, porciones_min, max_ingredientes):

    df_filtrado = df.copy()

    if vegano:
        df_filtrado = df_filtrado[df_filtrado["vegano"] == True]

    if vegetariano:
        df_filtrado = df_filtrado[df_filtrado["es_vegetariano"] == True]

    df_filtrado = df_filtrado[df_filtrado["precio_total"] <= precio_max]
    df_filtrado = df_filtrado[df_filtrado["tiempo"] <= tiempo_max]
    df_filtrado = df_filtrado[df_filtrado["porciones"] >= porciones_min]
    df_filtrado = df_filtrado[df_filtrado["num_ingredientes"] <= max_ingredientes]

    return df_filtrado


def traducir_receta(receta):
    prompt = f"""
    Traduce la siguiente recerta y responde SOLO en formato JSON válido.

    {{
        "ingredientes": ["...", "..."],
        "instrucciones": ["...", "..."]
    }}

    Ingredientes: {receta['ingredientes']}
    Instrucciones: {receta['pasos_ux']}
    """

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(response.choices[0].message.content)


def traducir_en(query):

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "user", "content": f"Traduce al inglés: {query}"}
        ]
    )
    return response.choices[0].message.content.strip()


def traducir_es(texto):
    prompt = f"""
    Traduce al español el siguiente nombre de receta.   
    Responde SOLO con el nombre traducido, sin explicaciones, sin comillas, sin texto adicional.

    Texto: {texto}
    """

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()


def get_embedding(text):
    return client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    ).data[0].embedding


### Recomendacion de postres
def buscar_recetas_base(query, df, top_n=3):

    # traducir a inglés
    query_en = traducir_en(query)

    # embedding del usuario
    query_emb = get_embedding(query_en)

    # matrices
    emb_text_matrix = np.array(df["embedding_instrucciones"].tolist())
    emb_ing_matrix = np.array(df["embedding_ingredientes"].tolist())

    # similitudes
    sim_text = cosine_similarity([query_emb], emb_text_matrix)[0]
    sim_ing = cosine_similarity([query_emb], emb_ing_matrix)[0]

    # combinación
    sim_final = 0.7 * sim_ing + 0.3 * sim_text

    # normalizar
    sim_final = (sim_final - sim_final.min()) / (sim_final.max() - sim_final.min() + 1e-8)

    # top resultados
    top_idx = np.argsort(sim_final)[-top_n:][::-1]
    resultados = df.iloc[top_idx].copy()

    # guardar score
    resultados["score"] = sim_final[top_idx]

    return resultados


def clasificar_confianza(valor):

    if valor >= 0.75:
        return "🟢 Alto"
    elif valor >= 0.5:
        return "🟡 Medio"
    else:
        return "🔴 Bajo"

### Descripcion general del postre
def generar_descripcion(receta):

    prompt = f"""
    Describe este postre en máximo 2 líneas, de forma atractiva, no menciones el nombre de la receta.

    Nombre: {receta}
    """
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()


### Analisis Nutricional
def analizar_receta_ia(receta):

    prompt = f"""
    Eres un experto analizando los porcentajes nutricionales de postres.
    Devuelve los cuatro puntos en lineas breves y claras, donde indique a que tipo de usuario no es recomendable consumir dicho postre,
    cantidades o porciones que se deben de disminuir o consumir, incluye recomendaciones y sustituciones de ingredientes.

    Analiza la siguiente receta:

    Nombre: {receta['nombre']}
    Ingredientes: {receta['ingredientes']}

    Información nutricional:
    - Calorías: {receta['calories']}
    - Azúcar: {receta['sugar_g']}
    - Carbohidratos: {receta['carbs_g']}
    - Proteínas: {receta['protein_g']}
    - Grasas: {receta['fat_g']}
    - Fibra: {receta['fiber_g']}

    Devuelve SOLO un JSON válido con esta estructura EXACTA:

    {{
      "alertas": [
        "texto corto",
        "texto corto"
      ],
      "nutricion": {{
        "calorias": "texto claro y breve",
        "azucar": "texto claro y breve",
        "carbohidratos": "texto claro y breve",
        "proteínas": "texto claro y breve"
        "grasas": "texto claro y breve"
        "fibra": "texto claro y breve"
      }},
      "recomendaciones": [
        "texto corto",
        "texto corto"
      ],
      "sustituciones": [
        "texto corto",
        "texto corto"
      ]
    }}

    Reglas:
    - NO agregues texto fuera del JSON
    - NO uses markdown
    - Respuestas claras, prácticas y específicas
    """

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    contenido = response.choices[0].message.content.strip()
    contenido = contenido.replace("```json", "").replace("```", "").strip()

    try:
        data = json.loads(contenido)
        return data
    except:
        return None
