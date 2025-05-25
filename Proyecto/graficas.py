import pandas as pd
import matplotlib.pyplot as plt

ventas = pd.read_csv("Proyecto/Venta.csv")
info_tiendas = pd.read_csv("Proyecto/dataset_exito_binario.csv")
metas = pd.read_csv("Proyecto/Meta_ventaactualizado.csv")

ventas.columns = ventas.columns.str.strip().str.upper()
info_tiendas.columns = info_tiendas.columns.str.strip().str.upper()
metas.columns = metas.columns.str.strip().str.upper()

ventas = ventas.merge(info_tiendas[['TIENDA_ID', 'ENTORNO_DES', 'EXITO', 'EXITO_BINARIO']], on='TIENDA_ID', how='left')
ventas = ventas.merge(metas[['ENTORNO_DES', 'META_VENTA']], on='ENTORNO_DES', how='left')

ventas['MES_AÑO'] = ventas['AÑO'].astype(str) + '-' + ventas['MES'].astype(str).str.zfill(2)

id_exito = ventas[ventas['EXITO_BINARIO'] == 1]['TIENDA_ID'].unique()[0]
id_no_exito = ventas[(ventas['EXITO_BINARIO'] == 0) & (ventas['EXITO'] < 40)]['TIENDA_ID'].unique()[0]

def graficar_tienda(tienda_id, titulo, archivo_png=None):
    df = ventas[ventas['TIENDA_ID'] == tienda_id].sort_values(['AÑO', 'MES'])
    entorno = df['ENTORNO_DES'].iloc[0]
    meta = df['META_VENTA'].iloc[0]

    plt.figure(figsize=(10, 5))
    plt.plot(df['MES_AÑO'], df['VENTA_TOTAL'], marker='o', label='Ventas mensuales')
    plt.axhline(y=meta, color='red', linestyle='--', label=f'Meta mensual ({entorno})')
    plt.title(f"{titulo} - Tienda {tienda_id} ({entorno})")
    plt.xlabel("Mes")
    plt.ylabel("Ventas")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    if archivo_png:
        plt.savefig(archivo_png)
        print(f" Gráfico guardado como: {archivo_png}")
    else:
        plt.show()

graficar_tienda(id_exito, " CASO DE ÉXITO", "grafico_exito.png")
graficar_tienda(id_no_exito, " CASO DE NO ÉXITO (< 40%)", "grafico_no_exito.png")
