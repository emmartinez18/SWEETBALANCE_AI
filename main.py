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
df["num_ingredientes"] = df["ingredientes"].apply(len)

st.sidebar.markdown("## 🔍 Filtros")

# Precio
usar_precio = st.sidebar.checkbox("💸 Filtrar por precio")
precio_max = st.sidebar.slider("Precio máximo", 0, 500, 100)

# Confianza
usar_confianza = st.sidebar.checkbox("🔎 Confianza del precio estimado")
confianza_min = st.sidebar.slider("Confianza mínima", 0.0, 1.0, 0.5)

# Tiempo
usar_tiempo = st.sidebar.checkbox("⏱ Filtrar por tiempo")
tiempo_max = st.sidebar.slider("Tiempo máximo", 0, 180, 60)

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

# Confianza
if usar_confianza:
    df_filtrado = df_filtrado[df_filtrado["confianza"] >= confianza_min]

# Tiempo
if usar_tiempo:
    df_filtrado = df_filtrado[df_filtrado["tiempo"] <= tiempo_max]

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
st.markdown("## 👋 Bienvenido a SweetBalance AI")
st.caption("Descubre deliciosas recetas de postres a tu gusto 🍰✨")
query = st.text_input("💬 Escribe el postre o tu ingrediente favorito:")

# CONTROL DE QUERY
if "opciones" not in st.session_state:
    st.session_state.opciones = {}

if "ultima_query" not in st.session_state:
    st.session_state.ultima_query = None

if "ultima_receta" not in st.session_state:
    st.session_state.ultima_receta = None


# BUSCADOR
if query:

    # SOLO recalcular si cambia query
    if query != st.session_state.ultima_query:

        st.session_state.ultima_query = query

        # reset estados
        st.session_state.receta_traducida = None
        st.session_state.analisis = None
        st.session_state.receta_seleccionada = None
        st.session_state.ultima_receta = None

        resultados = buscar_recetas_base(query, df, top_n=5)

        resultados = resultados[resultados["id"].isin(df_filtrado["id"])]

        # guardar opciones
        st.session_state.opciones = {
            row["nombre"]: row.to_dict()
            for _, row in resultados.iterrows()
        }

    opciones = st.session_state.opciones

    if not opciones:
        st.warning("No se encontraron recetas 😢")

    else:
        st.markdown("### 🔎 Te recomendamos estas opciones:")

        opciones_lista = list(opciones.keys())

        seleccion = st.selectbox(
            "Elige una opción 👇",
            opciones_lista,
            index=None,
            placeholder="Selecciona una receta...",
            key="selector_receta"
        )

        if seleccion:

            receta = opciones[seleccion]

            # RESET POR CAMBIO DE RECETA
            if st.session_state.ultima_receta != receta["id"]:
                st.session_state.receta_traducida = None
                st.session_state.analisis = None
                st.session_state.descripcion = None
                st.session_state.ultima_receta = receta["id"]

            # IMAGEN + INFO
            col1, col2 = st.columns([1,2])

            with col1:
                url = receta.get("imagen")
                if url and str(url).strip() != "":
                    st.image(url, width=550)
                else:
                    st.image("assets/default.jpg", width=550)   

            with col2:
                nombre_es = traducir_es(receta['nombre'])
                st.markdown(f"## 🍰 {nombre_es}")
                st.session_state.descripcion = generar_descripcion(receta["nombre"])
                st.caption(st.session_state.descripcion)

                st.markdown("")

                col1, col2 = st.columns(2)

                # PRECIO + CONFIANZA
                with col1:
                    st.markdown(
                        f"💸 **Precio estimado:** ${receta['precio_total']:.2f}  \n"
                        f"🔎 **Confianza del precio:** {clasificar_confianza(receta['confianza'])}")
 
                # TIEMPO + PORCIONES
                with col2:
                    st.markdown(
                        f"⏱ {receta['tiempo']} min  \n"
                        f"🍽 {int(receta['porciones'])} porciones")
               
                score = receta["health_score_norm"]
                if score > 0.8:
                    st.success("🟢 Opción balanceada")
                elif score > 0.5:
                    st.warning("🟡 Consumo moderado")
                else:
                    st.error("🔴 Alto en azúcar o grasas")

            # RECETA
            if "receta_traducida" not in st.session_state:
                st.session_state.receta_traducida = None

            if st.session_state.receta_traducida is None:
                with st.spinner("Preparando receta..."):
                    st.session_state.receta_traducida = traducir_receta(receta)

            receta_traducida = st.session_state.receta_traducida


            col1, col2 = st.columns([1,2])

            # INGREDIENTES
            with col1:

                st.markdown("### 🥗 Ingredientes")

                for ing in receta_traducida["ingredientes"]:
                    st.markdown(f"""
                    <div style="
                        display:flex;
                        align-items:center;
                        gap:10px;
                        background-color:#fff8f0;
                        padding:10px;
                        border-radius:12px;
                        margin-bottom:8px;
                        border-left:5px solid #ff9f68;
                    ">
                        <span style="font-size:18px;">🥄</span>
                        <span>{ing}</span>
                    </div>
                    """, unsafe_allow_html=True)

            # PREPARACIÓN
            with col2:
                
                st.markdown("### 📋 Preparación")

                st.markdown("""
                <div style="
                    background-color:#f8f9fa;
                    padding:15px;
                    border-radius:12px;
                    margin-bottom:12px;
                    border:1px solid #eee;
                ">
                """, unsafe_allow_html=True)

                for i, paso in enumerate(receta_traducida["instrucciones"], 1):
                    st.markdown(f"**-** {paso}")

                st.markdown("</div>", unsafe_allow_html=True)
                           
            # NUTRICIÓN
            if "analisis" not in st.session_state:
                st.session_state.analisis = None

            if st.session_state.analisis is None:
                with st.spinner("Analizando información nutricional..."):
                    st.session_state.analisis = analizar_receta_ia(receta)

            data = st.session_state.analisis

            # validación
            if data is None:
                st.error("No se pudo generar el análisis 😢")

            else:
                st.markdown("## 🥗 Información nutricional")

                col1, col2 = st.columns(2)

                # Sustituciones y Nutricion
                with col1:

                    st.markdown("## 🔄 Sustituciones")
                    for s in data["sustituciones"]:
                        st.write(f"• {s}")    

                    st.markdown("## 📊 Valores")

                    st.write(f"🔥 Calorías: {data['nutricion']['calorias']}")
                    st.write(f"🍬 Azúcar: {data['nutricion']['azucar']}")
                    st.write(f"🍞 Carbohidratos: {data['nutricion']['carbohidratos']}")
                    st.write(f"💪 Proteínas: {data['nutricion']['proteínas']}")
                    st.write(f"🧈 Grasas: {data['nutricion']['grasas']}")
                    st.write(f"🌿 Fibra: {data['nutricion']['fibra']}")

                 # Recomendaciones y Alertas
                with col2:
                    
                    st.markdown("## ⚠️ Alertas")
                    for alerta in data["alertas"]:
                        st.warning(alerta)

                    st.markdown("## ✅ Recomendaciones")
                    for r in data["recomendaciones"]:
                        st.success(r)

                    