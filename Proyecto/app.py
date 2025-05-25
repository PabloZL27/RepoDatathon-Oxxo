import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from difflib import get_close_matches
import folium
from streamlit_folium import st_folium
import requests

# Configuración inicial
st.set_page_config(page_title="Ubicaciones", layout="centered")

# Estilos personalizados
st.markdown("""
    <style>
    /* Fondo oscuro general */
    html, body, .stApp {
        background-color: #0e1117 !important;
        color: #ffffff !important;
        font-size: 18px !important;
    }
    
    .block-container {
        max-width: 95% !important;
        padding-left: 10rem !important;  /* Padding izquierdo */
        padding-right: 10rem !important; /* Padding derecho */
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }

    /* Contenedor principal con mayor ancho y espaciado */
    .block-container {
        max-width: 95% !important;
        padding: 2rem 3rem;
    }

    /* Input oscuro */
    .stTextInput > div > div > input,
    .stSelectbox > div,
    .stNumberInput > div {
        background-color: #262730;
        color: white;
        border-radius: 5px;
        font-size: 16px !important;
    }

    /* Botón con animación y color */
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        font-size: 16px !important;
        border: none;
        padding: 10px 24px;
        border-radius: 12px;
        transition: all 0.3s ease-in-out;
    }

    .stButton > button:hover {
        color: white;
        background-color: #45a049;
        transform: scale(1.03);
    }

    /* Título separado del navbar */
    .stApp h1 {
        margin-top: 3rem !important;
    }
    </style>
""", unsafe_allow_html=True)



st.markdown("""
    <div style="text-align: center; font-size: 48px; color: white; font-weight: bold; margin-top: 40px;">
        🗺️ <b>OXXO GeoInsights</b>
    </div>
    <div style="text-align: center; font-size: 28px; color: #cccccc; margin-bottom: 20px;">
        🌍 Explorador Geográfico de Nivel Socioeconómico
    </div>
    <hr style="border: 1px solid #444;">
""", unsafe_allow_html=True)

# Diccionario de nivel socioeconómico
escala_color = {
    "muy alto": "🔴 Nivel E",
    "alto": "🟠 Nivel D",
    "medio": "🟠 Nivel C",
    "bajo": "🟡 Nivel B",
    "muy bajo": "🟢 Nivel A"
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

    st.markdown("### 📌 Información adicional")
    tipo_entorno = st.selectbox("Tipo de entorno", ["Urbano", "Suburbano", "Rural"])
    metros_cuadrados = st.number_input("Tamaño del terreno (m²)", min_value=0, step=1)

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

if lat and lon:
    folium.Marker([lat, lon], popup="Ubicación seleccionada").add_to(m)
    folium.Circle([lat, lon], radius=poblacion_cercana * 1000, color="blue", fill=True).add_to(m)

def obtener_competencia(lat, lon):
    # Ejemplo con Google Places API
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lon}&radius=5000&type=store&key=YOUR_API_KEY"
    response = requests.get(url)
    return response.json()

competencia = obtener_competencia(lat, lon)
st.write("Negocios cercanos:", competencia)

with st.expander("ℹ️ Cómo usar esta aplicación"):
    st.write("""
        1. Selecciona una ubicación en el mapa o ingresa las coordenadas manualmente.
        2. Proporciona información adicional como tipo de entorno y tamaño del terreno.
        3. Consulta el potencial de éxito y otros datos relevantes.
    """)
