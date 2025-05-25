import joblib
import pandas as pd

modelo_binario = joblib.load("Proyecto/Modelo_Binario.pkl")
modelo_regresion = joblib.load("Proyecto/Modelo_Porcentajes.pkl")
preprocesador = joblib.load("Proyecto/preprocesador.pkl")
threshold = joblib.load("Proyecto/umbral_optimo.pkl")

print("Introduce los siguientes datos de la tienda:")
longitud = float(input("LONGITUD_NUM: "))
latitud = float(input("LATITUD_NUM: "))
entorno = input("ENTORNO_DES: ")
mts2 = float(input("MTS2VENTAS_NUM: "))
nivel_socio = input("NIVELSOCIOECONOMICO_DES: ")
plaza = input("PLAZA_CVE: ")
ubicacion = input("LID_UBICACION_TIENDA: ")

entrada = pd.DataFrame([{
    'LONGITUD_NUM': longitud,
    'LATITUD_NUM': latitud,
    'ENTORNO_DES': entorno,
    'MTS2VENTAS_NUM': mts2,
    'NIVELSOCIOECONOMICO_DES': nivel_socio,
    'PLAZA_CVE': plaza,
    'LID_UBICACION_TIENDA': ubicacion
}])

X_clasif_proc = preprocesador.transform(entrada)
prob = modelo_binario.predict_proba(X_clasif_proc)[:, 1][0]
exito_binario = int(prob >= threshold)

entrada['exito_binario'] = exito_binario

porcentaje_exito = modelo_regresion.predict(entrada)[0]

print("\n RESULTADO:")
print(f"¿Tendrá éxito la tienda?: {'Sí (1)' if exito_binario else 'No (0)'}")
print(f"Porcentaje estimado de éxito: {porcentaje_exito:.2f}%")
