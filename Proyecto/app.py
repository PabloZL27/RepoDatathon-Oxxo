import streamlit as st
import pandas as pd

# Título de la app
st.title("Consulta de Nivel Socioeconómico en Nuevo León")

# Cargar el archivo Excel
@st.cache_data
def cargar_datos():
    df = pd.read_excel("NivelSocioEconomicoNL.xlsx")
    df["Nombre del municipio"] = df["Nombre del municipio"].str.strip().str.lower()
    return df

df = cargar_datos()

# Diccionario visual
escala_color = {
    "muy alto": "🔴 Nivel E",
    "alto": "🔴 Nivel D",
    "medio": "🟠 Nivel C",
    "bajo": "🟡 Nivel B",
    "muy bajo": "🟢 Nivel A"
}

# Input del usuario
municipio_input = st.text_input("Ingresa el nombre del municipio de Nuevo León:")

if municipio_input:
    municipio = municipio_input.strip().lower()
    resultado = df[df["Nombre del municipio"] == municipio]

    if not resultado.empty:
        grado_raw = resultado.iloc[0]["Grado de marginación, 2020"]
        grado = grado_raw.strip().lower()
        visual = escala_color.get(grado, grado_raw)

        st.success(f"📍 **Municipio:** {municipio.title()}")
        st.markdown(f"🏷️ **Nivel socioeconómico:** {visual}")
    else:
        st.error("❌ Municipio no encontrado.")
