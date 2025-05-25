import pandas as pd
import joblib

df = pd.read_csv("Proyecto/DIM_TIENDA_TEST.csv")

modelo_clasif = joblib.load("Proyecto/Modelo_Binario.pkl")
modelo_reg = joblib.load("Proyecto/Modelo_Porcentajes.pkl")
preprocesador = joblib.load("Proyecto/preprocesador.pkl")
threshold = joblib.load("Proyecto/umbral_optimo.pkl")

features_clasif = [
    'LONGITUD_NUM','LATITUD_NUM',
    'ENTORNO_DES','MTS2VENTAS_NUM',
    'NIVELSOCIOECONOMICO_DES',
    'PLAZA_CVE','LID_UBICACION_TIENDA'
]

features_reg = [
    'LONGITUD_NUM','LATITUD_NUM',
    'ENTORNO_DES','MTS2VENTAS_NUM',
    'NIVELSOCIOECONOMICO_DES','LID_UBICACION_TIENDA','exito_binario'
]

X_clasif = df[features_clasif]
X_proc = preprocesador.transform(X_clasif)
probs = modelo_clasif.predict_proba(X_proc)[:, 1]
df["exito_binario"] = (probs >= threshold).astype(int)

X_reg = df[features_reg]
df["prediccion_exito"] = modelo_reg.predict(X_reg)

df.to_csv("DIM_TIENDA_TEST_con_predicciones.csv", index=False)
print(" Archivo generado: DIM_TIENDA_TEST_con_predicciones.csv")
