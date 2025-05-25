import pandas as pd

# Carga tu dataset actual
df = pd.read_csv('Proyecto/DIM_TIENDA_Con_Exito.csv')

print(df['Exito'].isna().sum())

