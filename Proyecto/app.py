import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from difflib import get_close_matches
import folium
from streamlit_folium import st_folium

# Configuración inicial
st.set_page_config(page_title="Ubicaciones", layout="centered")
st.title("🗺️ Ubicación y Datos Demográficos")

# Diccionario de nivel socioeconómico
escala_color = {
    "muy alto": "🔴 Nivel E (muy alta marginación)",
    "alto": "🔴 Nivel D (alta marginación)",
    "medio": "🟠 Nivel C (media marginación)",
    "bajo": "🟡 Nivel B (baja marginación)",
    "muy bajo": "🟢 Nivel A (muy baja marginación)"
}

# Cargar Excel de nivel socioeconómico
@st.cache_data
def cargar_datos():
    df = pd.read_excel("NivelSocioEconomicoNL.xlsx")
    df["Nombre del municipio"] = df["Nombre del municipio"].str.strip().str.lower()
    return df

df_excel = cargar_datos()

# Geocodificación inversa con timeout aumentado
def obtener_lugar_desde_coordenadas(lat, lon):
    try:
        geolocator = Nominatim(user_agent="streamlit-geoapp", timeout=10)
        location = geolocator.reverse((lat, lon), language="es")
        if location:
            address = location.raw.get("address", {})
            municipio = (
                address.get("municipality")
                or address.get("town")
                or address.get("city")
                or address.get("county")
                or address.get("state")
            )
            return municipio.lower().strip(), location.address
        else:
            return None, "No se pudo obtener información del lugar."
    except Exception as e:
        return None, f"Error: {e}"

# Mapa centrado en Nuevo León
st.subheader("Da clic en el mapa o ingresa las coordenadas manualmente")

# Crear columnas para dividir el espacio
col1, col2 = st.columns(2)

# Entrada manual de coordenadas
with col1:
    st.markdown("### 📌 Ingresar coordenadas manualmente")
    lat_manual = st.text_input("Latitud", placeholder="Ejemplo: 25.6714")
    lon_manual = st.text_input("Longitud", placeholder="Ejemplo: -100.3090")
    boton_manual = st.button("Buscar con coordenadas ingresadas")

# Mapa interactivo
with col2:
    st.markdown("### 🗺️ Seleccionar coordenadas en el mapa")
    m = folium.Map(location=[25.6714, -100.3090], zoom_start=7, control_scale=True)
    st_data = st_folium(m, height=500, width=700)

# Procesar clic en el mapa o entrada manual
lat, lon = None, None

if boton_manual and lat_manual and lon_manual:
    try:
        lat = float(lat_manual)
        lon = float(lon_manual)
    except ValueError:
        st.error("❌ Por favor, ingresa valores numéricos válidos para latitud y longitud.")

elif st_data and st_data.get("last_clicked"):
    lat = st_data["last_clicked"]["lat"]
    lon = st_data["last_clicked"]["lng"]

# Procesar las coordenadas obtenidas
if lat is not None and lon is not None:
    with st.spinner("🔄 Obteniendo municipio desde coordenadas..."):
        municipio_detectado, descripcion = obtener_lugar_desde_coordenadas(lat, lon)

    st.markdown(f"🧭 **Coordenadas:** Latitud: `{lat:.6f}` | Longitud: `{lon:.6f}`")

    if municipio_detectado:
        st.success(f"📌 Municipio o localidad detectada: **{municipio_detectado.title()}**")
        st.markdown(f"📍 Dirección aproximada: `{descripcion}`")

        # Buscar en Excel
        resultado = df_excel[df_excel["Nombre del municipio"] == municipio_detectado]

        # Coincidencia aproximada si no hay directa
        if resultado.empty:
            posibles = df_excel["Nombre del municipio"].tolist()
            match = get_close_matches(municipio_detectado, posibles)
            if match:
                municipio_detectado = match[0]
                resultado = df_excel[df_excel["Nombre del municipio"] == municipio_detectado]

        if not resultado.empty:
            grado_raw = resultado.iloc[0]["Grado de marginación, 2020"]
            grado = grado_raw.strip().lower()
            visual = escala_color.get(grado, grado_raw)
            st.markdown(f"🏷️ **Nivel socioeconómico:** {visual}")
        else:
            st.warning("⚠️ Municipio no encontrado en el archivo socioeconómico.")
    else:
        st.error(f"❌ {descripcion}")
else:
    st.info("Haz clic en el mapa o ingresa las coordenadas manualmente para consultar.")
