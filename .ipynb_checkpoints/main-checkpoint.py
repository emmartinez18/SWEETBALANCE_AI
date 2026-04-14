
# 🎨 Tema pastel
import streamlit as st
st.set_page_config(
    page_title="SweetBalance AI",
    layout="centered"
)

# 🔴 FORZAR ESTILO CON HTML GLOBAL
st.markdown("""
<style>
html, body, [class*="css"]  {
    background-color: #FF4D6D !important;
}

[data-testid="stAppViewContainer"] {
    background-color: #FF4D6D !important;
}

section.main > div {
    background-color: transparent !important;
}
</style>
""", unsafe_allow_html=True)


st.title("🍰 SweetBalance AI")
st.caption("Recomendaciones nutricionales de postres")

prompt = st.text_input("¿Qué postre te gustaría preparar?")

profile = st.selectbox(
    "Selecciona tu perfil",
    ["Dieta", "Salud", "Bebida", "Postre"]
)

if prompt:
    st.success(f"🍓 Recomendación para: {prompt} ({profile})")
else:
    st.info("Por favor, ingresa un postre")