import pandas as pd
import os

script_dir = os.path.dirname(os.path.abspath(__file__))

path_tiendas = os.path.join(script_dir, 'DIM_TIENDA.csv')
path_meta    = os.path.join(script_dir, 'Meta_ventaactualizado.csv')
path_ventas  = os.path.join(script_dir, 'Venta.csv')

df_tiendas = pd.read_csv(path_tiendas, usecols=['TIENDA_ID', 'ENTORNO_DES'])
df_meta    = pd.read_csv(path_meta)   
df_ventas  = pd.read_csv(path_ventas)         


df = (
    df_ventas
    .merge(df_tiendas, on='TIENDA_ID', how='left')    
    .merge(df_meta,    on='ENTORNO_DES', how='left')  
)

missing_meta = df['Meta_venta'].isna().sum()
print(f"Filas sin Meta_venta asignada: {missing_meta}")

df['cumple_meta'] = (df['VENTA_TOTAL'] >= df['Meta_venta']).astype(int)


df_exito = (
    df
    .groupby('TIENDA_ID')['cumple_meta']
    .mean()                  
    .mul(100)          
    .round(1)             
    .reset_index()
    .rename(columns={'cumple_meta': 'Exito'})
)

df_full_tiendas = pd.read_csv(path_tiendas) 
df_final = df_full_tiendas.merge(df_exito, on='TIENDA_ID', how='left')

output_path = os.path.join(script_dir, 'DIM_TIENDA_Con_Exito.csv')
df_final.to_csv(output_path, index=False)

print(" Generado 'DIM_TIENDA_Con_Exito.csv' con la columna Exito.")
