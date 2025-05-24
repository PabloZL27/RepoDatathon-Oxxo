import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Título de la app
st.title("📊 Visualización de Datos")

# Carga de datos
st.subheader("Datos cargados")
df = pd.read_csv("../Datos/DIM_TIENDA_TEST.csv")  # Reemplaza por tu archivo
st.dataframe(df)

# Gráfica simple
st.subheader("Gráfico de barras")
columna = st.selectbox("Selecciona una columna numérica", df.select_dtypes(include='number').columns)
fig, ax = plt.subplots()
df[columna].value_counts().plot(kind='bar', ax=ax)
st.pyplot(fig)
