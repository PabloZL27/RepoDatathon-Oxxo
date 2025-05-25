import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from difflib import get_close_matches
import folium
from streamlit_folium import st_folium
import requests
import joblib

# Configuración inicial
st.set_page_config(page_title="Ubicaciones", layout="centered")

# Estilos personalizados
st.markdown("""
    <style>
    html, body, .stApp {
        background-color: #0e1117 !important;
        color: #ffffff !important;
        font-size: 18px !important;
    }
    .block-container {
        max-width: 95% !important;
        padding-left: 10rem !important;
        padding-right: 10rem !important;
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    .stTextInput > div > div > input,
    .stSelectbox > div,
    .stNumberInput > div {
        background-color: #262730;
        color: white;
        border-radius: 5px;
        font-size: 16px !important;
    }
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
    .stApp h1 {
        margin-top: 3rem !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div style="text-align: center; font-size: 48px; color: white; font-weight: bold; margin-top: 1px; margin-bottom: 20px;">
        <b>OXXO GeoInsights</b>
    </div>
    <div style="text-align: center; font-size: 28px; color: #cccccc; margin-bottom: 20px;">
        Explorador Geográfico de Nivel Socioeconómico
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

@st.cache_data
def cargar_datos():
    df = pd.read_excel("NivelSocioEconomicoNL.xlsx")
    df["Nombre del municipio"] = df["Nombre del municipio"].str.strip().str.lower()
    return df

df_excel = cargar_datos()

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

# Sección de inputs
st.subheader("Da click en el mapa o ingresa las coordenadas manualmente")
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Ingresar coordenadas manualmente")
    lat_manual = st.text_input("Latitud", placeholder="Ejemplo: 25.6714")
    lon_manual = st.text_input("Longitud", placeholder="Ejemplo: -100.3090")
    boton_manual = st.button("Buscar con coordenadas ingresadas")

with col2:
    st.markdown("### Seleccionar coordenadas en el mapa")
    m = folium.Map(location=[25.6714, -100.3090], zoom_start=7, control_scale=True)
    st_data = st_folium(m, height=500, width=700)

lat, lon = None, None
if boton_manual and lat_manual and lon_manual:
    try:
        lat = float(lat_manual)
        lon = float(lon_manual)
    except ValueError:
        st.error("Por favor, ingresa valores numéricos válidos para latitud y longitud.")
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
        resultado = df_excel[df_excel["Nombre del municipio"] == municipio_detectado]

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

            # ⚡ PREDICCIÓN DE ÉXITO DE TIENDA
            st.markdown("---")
            st.subheader("🔍 Predicción de Éxito de Tienda OXXO")

            # Crear un formulario para agrupar los campos y el botón
            with st.form("form_prediccion"):
                plaza = st.text_input("Código de plaza (1-6)", placeholder="Ejemplo: 1")
                ubicacion = st.selectbox("Ubicación Tienda", ["UT_CARRETERA_GAS", "UT_DENSIDAD", "UT_GAS_URBANA", "UT_TRAFICO_PEATONAL", "UT_TRAFICO_VEHICULAR"])
                tipo_entorno = st.selectbox("Tipo de entorno", ["Base", "Hogar", "Peatonal", "Receso"])
                metros_cuadrados = st.number_input("Tamaño del terreno (m²)", min_value=0, step=1)
                
                # Botón para enviar el formulario
                boton_predecir = st.form_submit_button("Predecir éxito")

            # Procesar la predicción si se envía el formulario
            if boton_predecir:
                if not plaza or not ubicacion:
                    st.warning("⚠️ Por favor completa todos los campos para realizar la predicción.")
                else:
                    try:
                        modelo_binario = joblib.load("Modelo_Binario.pkl")
                        modelo_regresion = joblib.load("Modelo_Porcentajes.pkl")
                        preprocesador = joblib.load("preprocesador.pkl")
                        threshold = joblib.load("umbral_optimo.pkl")

                        entrada = pd.DataFrame([{
                            'LONGITUD_NUM': lon,
                            'LATITUD_NUM': lat,
                            'ENTORNO_DES': tipo_entorno,
                            'MTS2VENTAS_NUM': metros_cuadrados,
                            'NIVELSOCIOECONOMICO_DES': grado.title(),
                            'PLAZA_CVE': plaza,
                            'LID_UBICACION_TIENDA': ubicacion
                        }])

                        X_proc = preprocesador.transform(entrada)
                        prob = modelo_binario.predict_proba(X_proc)[:, 1][0]
                        exito_binario = int(prob >= threshold)

                        entrada['exito_binario'] = exito_binario
                        porcentaje_exito = modelo_regresion.predict(entrada)[0]

                        st.success("✅ Predicción realizada con éxito:")
                        st.markdown(f"📈 **Probabilidad de éxito**: {'Alta' if exito_binario else 'Baja'} ({prob*100:.2f}%)")
                        st.markdown(f"📊 **Porcentaje estimado de cumplimiento de meta cada mes**: `{porcentaje_exito:.2f}%`")

                    except Exception as e:
                        st.error(f"❌ Error al realizar la predicción: {e}")

        else:
            st.warning("⚠️ Municipio no encontrado en el archivo socioeconómico.")
    else:
        st.error(f"❌ {descripcion}")
else:
    st.info("Haz clic en el mapa o ingresa las coordenadas manualmente para consultar.")

if lat and lon:
    folium.Marker([lat, lon], popup="Ubicación seleccionada").add_to(m)

with st.expander("ℹ️ Cómo usar esta aplicación"):
    st.write("""
        1. Selecciona una ubicación en el mapa o ingresa las coordenadas manualmente.
        2. Proporciona información adicional como tipo de entorno y tamaño del terreno.
        3. Consulta el potencial de éxito y otros datos relevantes.
    """)
    
st.markdown("---")
st.subheader("🔎 Información Adicional")

# Mostrar dos imágenes en columnas
col1, col2 = st.columns(2)

with col1:
    st.image("img/CasoExito.jpeg", caption="Casos de éxito", use_container_width=True)

with col2:
    st.image("img/CasoExito2.jpeg", caption="Casos de éxito", use_container_width=True)
