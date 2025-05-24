import pandas as pd

# 1) Cargo los datos
df_tiendas = pd.read_csv('DIM_TIENDA.csv', usecols=['TIENDA_ID', 'ENTORNO_DES'])
df_meta    = pd.read_csv('Meta_ventaactualizado.csv')   # columnas: ENTORNO_DES, Meta_venta
df_ventas  = pd.read_csv('Venta.csv')                  # columnas: TIENDA_ID, MES_ID, VENTA_TOTAL

# 2) Uno ventas ↔ tiendas ↔ metas
df = (
    df_ventas
    .merge(df_tiendas, on='TIENDA_ID', how='left')     # trae ENTORNO_DES a cada venta
    .merge(df_meta,    on='ENTORNO_DES', how='left')   # trae la Meta_venta según el entorno
)

# Verifico cuántas filas quedaron sin meta (opcional)
missing_meta = df['Meta_venta'].isna().sum()
print(f"Filas sin Meta_venta asignada: {missing_meta}")

# 3) Flag de cumplimiento mes a mes (1 si VENTA_TOTAL ≥ Meta_venta, 0 si no)
df['cumple_meta'] = (df['VENTA_TOTAL'] >= df['Meta_venta']).astype(int)

# 4) Calcular % de éxito por tienda
df_exito = (
    df
    .groupby('TIENDA_ID')['cumple_meta']
    .mean()                   # promedio de 0/1 → proporción de meses cumplidos
    .mul(100)                 # al 100%
    .round(1)                 # redondear a 1 decimal
    .reset_index()
    .rename(columns={'cumple_meta': 'Exito'})
)

# 5) Unir ese porcentaje al catálogo original (para conservar todas las columnas)
df_final = pd.read_csv('DIM_TIENDA.csv').merge(df_exito, on='TIENDA_ID', how='left')

# 6) Guardar el nuevo CSV
df_final.to_csv('DIM_TIENDA_Con_Exito.csv', index=False)

print("📈 Generado 'DIM_TIENDA_Con_Exito.csv' con la columna Exito.")
