
import streamlit as st
from modelo import *
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
import os
import json
from PIL import Image
import streamlit_shadcn_ui as st_yled

st.markdown(
    """
    <style>
    /* Fondo general */
    .stApp {
        background-color: #F5EFE6 !important;  /* crema suave */
    }

    /* Contenedor principal */
    .main {
        background-color: transparent !important;
    }

    /* Texto general */
    body, p, div {
        color: #3E3E3E !important;  /* gris oscuro elegante */
    }

    /* Inputs */
    .stTextInput input {
        background-color: #FFFFFF !important;
        color: #3E3E3E !important;
        border-radius: 10px;
        border: 1px solid #E8D8C4;
    }

    /* Selectbox */
    .stSelectbox div {
        background-color: #FFFFFF !important;
        color: #3E3E3E !important;
        border-radius: 10px;
        border: 1px solid #E8D8C4;
    }

    /* Botones */
    .stButton button {
        background-color: #A67C52 !important;  /* café */
        color: white !important;
        border-radius: 10px;
        border: none;
    }

    .stButton button:hover {
        background-color: #8C6239 !important;  /* café más oscuro */
    }

    /* Alertas (info / success) */
    .stAlert {
        background-color: #FFFFFF !important;
        color: #3E3E3E !important;
        border-radius: 12px;
        border: 1px solid #E8D8C4;
    }

    /* Títulos */
    h1, h2, h3 {
        color: #6B4F3A !important;  /* chocolate */
    }
    </style>
    """,
    unsafe_allow_html=True)

st.markdown(
    """
    <style>
    /* Fondo */
    [data-testid="stSidebar"] {
        background-color: #E8D8C4;
    }

    /* Contenedor del sidebar */
    [data-testid="stSidebar"] > div:first-child {
        display: flex;
        flex-direction: column;
        justify-content: center;  /* 👈 centra vertical */
        align-items: center;      /* 👈 centra horizontal */
        height: 100vh;
    }

    /* Centrar imagen */
    [data-testid="stSidebar"] .stImage {
        display: flex;
        justify-content: center;
    }

    /* Centrar caption */
    [data-testid="stSidebar"] .stCaption {
        text-align: center;
        color: #6b6b6b;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown(
    """
    <style>

    /* Caja principal del selectbox */
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #333333 !important;
        border-radius: 12px;
        border: 1px solid #ddd;
        padding: 5px;
    }

    /* Texto seleccionado */
    div[data-baseweb="select"] span {
        color: #333333 !important;
        font-weight: 500;
    }

    /* Dropdown (lista) */
    ul[role="listbox"] {
        background-color: #ffffff !important;
        border-radius: 10px;
        border: 1px solid #ddd;
    }

    /* Opciones dentro del dropdown */
    li[role="option"] {
        color: #333333 !important;
    }

    /* Hover */
    li[role="option"]:hover {
        background-color: #f5f5f5 !important;
    }

    </style>
    """, unsafe_allow_html=True)

st.markdown(
    """
    <style>
    img {
        display: block;
        margin-left: auto;
        margin-right: auto;
        max-width: 300px;
    }
    </style>
    """, unsafe_allow_html=True)

logop = Image.open("assets/logop.jpeg")
logo = Image.open("assets/logo.png")

st.set_page_config(
    layout = "wide",
    page_title = "SweetBalance AI",
    page_icon = logop)

st.sidebar.image(logo, caption = "El lado dulce, ahora más consciente")

# CARGA DE DATOS
df = cargar_datos()

st.sidebar.markdown("## 🔍 Filtros")

# Precio
usar_precio = st.sidebar.checkbox("💸 Filtrar por precio")
precio_max = st.sidebar.slider("Precio máximo", 0, 150, 100)

# Tiempo
usar_tiempo = st.sidebar.checkbox("⏱ Filtrar por tiempo")
tiempo_max = st.sidebar.slider("Tiempo máximo", 0, 180, 60)

# Confianza
usar_confianza = st.sidebar.checkbox("🔎 Filtrar por confianza")
confianza_min = st.sidebar.slider("Confianza mínima", 0.0, 1.0, 0.5)

# Dieta
vegano = st.sidebar.checkbox("🌱 Vegano")
vegetariano = st.sidebar.checkbox("🥗 Vegetariano")

# Porciones
usar_porciones = st.sidebar.checkbox("🍽 Filtrar por porciones")
porciones_min = st.sidebar.slider("Porciones mínimas", 1, 10, 2)

# Ingredientes
usar_ingredientes = st.sidebar.checkbox("🔢 Filtrar por ingredientes")
max_ingredientes = st.sidebar.slider("Máx ingredientes", 1, 20, 10)


df_filtrado = df.copy()

# Precio
if usar_precio:
    df_filtrado = df_filtrado[df_filtrado["precio_total"] <= precio_max]

# Tiempo
if usar_tiempo:
    df_filtrado = df_filtrado[df_filtrado["tiempo"] <= tiempo_max]

# Confianza
if usar_confianza:
    df_filtrado = df_filtrado[df_filtrado["confianza"] >= confianza_min]

# Dieta
if vegano:
    df_filtrado = df_filtrado[df_filtrado["vegano"] == True]

if vegetariano:
    df_filtrado = df_filtrado[df_filtrado["es_vegetariano"] == True]

# Porciones
if usar_porciones:
    df_filtrado = df_filtrado[df_filtrado["porciones"] >= porciones_min]

# Ingredientes
if usar_ingredientes:
    df_filtrado = df_filtrado[df_filtrado["num_ingredientes"] <= max_ingredientes]


# 🔍 INPUT
query = st.text_input("🍰 ¿Qué postre te gustaría preparar?")

# =========================
# 🧠 CONTROL DE QUERY
# =========================
if "ultima_query" not in st.session_state:
    st.session_state.ultima_query = None

if query != st.session_state.ultima_query:
    st.session_state.receta_traducida = None
    st.session_state.analisis = None
    st.session_state.receta_seleccionada = None
    st.session_state.ultima_receta = None  # 🔥 importante
    st.session_state.ultima_query = query

# =========================
# 🔎 BUSCADOR
# =========================
if query:
    resultados = buscar_recetas_base(query, df, top_n=5)

    # 🔥 aplicar filtros
    resultados = resultados[resultados["id"].isin(df_filtrado["id"])]

    if resultados.empty:
        st.warning("No se encontraron recetas 😢")

    else:
        st.markdown("### 🔎 Te recomendamos estas opciones:")

        opciones = {
            row["nombre"]: row.to_dict()
            for _, row in resultados.iterrows()
        }

        seleccion = st.selectbox(
            "Elige una opción 👇",
            ["Selecciona una receta..."] + list(opciones.keys())
        )

        if seleccion != "Selecciona una receta...":

            receta = opciones[seleccion]

            # =========================
            # 🧠 RESET POR CAMBIO DE RECETA
            # =========================
            if "ultima_receta" not in st.session_state:
                st.session_state.ultima_receta = None

            if st.session_state.ultima_receta != receta["id"]:
                st.session_state.receta_traducida = None
                st.session_state.analisis = None
                st.session_state.ultima_receta = receta["id"]

            # =========================
            # 🖼 IMAGEN + INFO
            # =========================
            col1, col2 = st.columns([1,2])

            with col1:
                url = receta.get("imagen")
                if url and str(url).strip() != "":
                    st.image(url, width=250)
                else:
                    st.image("assets/default.jpg", width=250)

            with col2:
                st.markdown(f"## 🍰 {receta['nombre']}")
                st.markdown(
                    f"💸 ${receta['precio_total']:.2f} | 🔎 {clasificar_confianza(receta['confianza'])}"
                )

            # =========================
            # 🍰 RECETA
            # =========================
            if "receta_traducida" not in st.session_state:
                st.session_state.receta_traducida = None

            if st.session_state.receta_traducida is None:
                with st.spinner("Preparando receta..."):
                    st.session_state.receta_traducida = traducir_receta(receta)

            receta_traducida = st.session_state.receta_traducida

            st.markdown("### 🥗 Ingredientes")
            for ing in receta_traducida["ingredientes"]:
                st.write(f"• {ing}")

            st.markdown("### 📋 Preparación")
            for i, paso in enumerate(receta_traducida["instrucciones"], 1):
                st.write(f"{i}. {paso}")

            # =========================
            # 🥗 NUTRICIÓN
            # =========================
            if "analisis" not in st.session_state:
                st.session_state.analisis = None

            if st.session_state.analisis is None:
                with st.spinner("Analizando información nutricional..."):
                    st.session_state.analisis = analizar_receta_ia(receta)

            data = st.session_state.analisis

            # 🚨 validación importante
            if data is None:
                st.error("No se pudo generar el análisis 😢")

            else:
                st.markdown("---")
                st.markdown("## 🥗 Información nutricional")

                st.markdown("### ⚠️ Alertas")
                for alerta in data["alertas"]:
                    st.warning(alerta)

                st.markdown("### 📊 Valores")

                st.write(f"🔥 Calorías: {data['nutricion']['calorias']}")
                st.write(f"🍬 Azúcar: {data['nutricion']['azucar']}")
                st.write(f"🍞 Carbohidratos: {data['nutricion']['carbohidratos']}")
                st.write(f"💪 Proteínas: {data['nutricion']['proteínas']}")
                st.write(f"🧈 Grasas: {data['nutricion']['grasas']}")
                st.write(f"🌿 Fibra: {data['nutricion']['fibra']}")

                st.markdown("### ✅ Recomendaciones")
                for r in data["recomendaciones"]:
                    st.success(r)

                st.markdown("### 🔄 Sustituciones")
                for s in data["sustituciones"]:
                    st.write(f"• {s}")