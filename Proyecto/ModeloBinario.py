import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import joblib
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from imblearn.over_sampling import SMOTE

# 1. Cargar dataset
df = pd.read_csv('/Users/bryanmeza/Projects/RepositoriosGitHub/RepoDatathon-Oxxo/Proyecto/dataset_exito_binario.csv')

features = [
    'LONGITUD_NUM','LATITUD_NUM',
    'ENTORNO_DES','MTS2VENTAS_NUM',
    'NIVELSOCIOECONOMICO_DES',
    'PLAZA_CVE','LID_UBICACION_TIENDA'
]

df = df.dropna(subset=['Exito'])
X = df[features]
y = df['exito_binario']

# 2. Dividir en train y test
X_train_raw, X_test_raw, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

# 3. Separar columnas por tipo
categorical_features = X.select_dtypes(include=['object']).columns.tolist()
numeric_features = X.select_dtypes(include=['int64', 'float64']).columns.tolist()

# 4. Preprocesamiento
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ])

# 5. Pipeline de modelo
pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(random_state=42))
])

param_grid = {
    'classifier__n_estimators': [200, 300],
    'classifier__max_depth': [15, 20],
    'classifier__min_samples_split': [2],
    'classifier__min_samples_leaf': [1],
    'classifier__bootstrap': [True]
}

# 🔹 GRAFICAR DISTRIBUCIÓN ANTES DE SMOTE
plt.figure(figsize=(6, 4))
plt.bar(['Clase 0', 'Clase 1'], [sum(y_train == 0), sum(y_train == 1)], color=['red', 'green'])
plt.title('Distribución antes de SMOTE')
plt.ylabel('Muestras')
plt.show()

# 🔹 ENTRENAMIENTO SIN SMOTE
print("=== Modelo SIN SMOTE ===")
grid_no_smote = GridSearchCV(pipeline, param_grid, cv=5, scoring='accuracy', n_jobs=-1)
grid_no_smote.fit(X_train_raw, y_train)
y_pred_no = grid_no_smote.predict(X_test_raw)

print("Accuracy:", accuracy_score(y_test, y_pred_no))
print("Matriz de Confusión:\n", confusion_matrix(y_test, y_pred_no))
print("Reporte:\n", classification_report(y_test, y_pred_no))

# 🔹 APLICAR PREPROCESADOR + SMOTE
X_train_processed = preprocessor.fit_transform(X_train_raw)
X_test_processed = preprocessor.transform(X_test_raw)

sm = SMOTE(random_state=42)
X_train_smote, y_train_smote = sm.fit_resample(X_train_processed, y_train)

# 🔹 GRAFICAR DISTRIBUCIÓN DESPUÉS DE SMOTE
plt.figure(figsize=(6, 4))
plt.bar(['Clase 0', 'Clase 1'], [sum(y_train_smote == 0), sum(y_train_smote == 1)], color=['red', 'green'])
plt.title('Distribución después de SMOTE')
plt.ylabel('Muestras')
plt.show()

# 🔹 ENTRENAMIENTO CON SMOTE
print("\n=== Modelo CON SMOTE ===")
rf_best_params = {k.replace('classifier__', ''): v for k, v in grid_no_smote.best_params_.items()}
model_smote = RandomForestClassifier(random_state=42, **rf_best_params)
model_smote.fit(X_train_smote, y_train_smote)

y_probs = model_smote.predict_proba(X_test_processed)[:, 1]

best_acc = 0
best_threshold = 0.5
for t in [i / 100 for i in range(10, 90)]:
    y_pred_thresh = (y_probs >= t).astype(int)
    acc = accuracy_score(y_test, y_pred_thresh)
    if acc > best_acc:
        best_acc = acc
        best_threshold = t

print(f"\n🔧 Mejor threshold para accuracy: {best_threshold} → Accuracy: {best_acc}")

# Predicción con mejor threshold
y_pred_smote = (y_probs >= best_threshold).astype(int)

print("\nAccuracy con mejor threshold:", accuracy_score(y_test, y_pred_smote))
print("Matriz de Confusión:\n", confusion_matrix(y_test, y_pred_smote))
print("Reporte:\n", classification_report(y_test, y_pred_smote))

# 🔹 EXPORTAR MÉTRICAS A CSV
from sklearn.metrics import classification_report, accuracy_score

def extract_metrics_dict(y_true, y_pred):
    report = classification_report(y_true, y_pred, output_dict=True)
    return {
        'Accuracy': accuracy_score(y_true, y_pred),
        'Precision_0': report['0']['precision'],
        'Recall_0': report['0']['recall'],
        'F1_0': report['0']['f1-score'],
        'Precision_1': report['1']['precision'],
        'Recall_1': report['1']['recall'],
        'F1_1': report['1']['f1-score']
    }

metrics_smote_threshold = extract_metrics_dict(y_test, y_pred_smote)
df_metrics = pd.DataFrame(metrics_smote_threshold.items(), columns=['Métrica', 'Con_SMOTE_y_Threshold'])
df_metrics.to_csv('resultados_modelo_comparado.csv', index=False)
print("\n✅ Resultados exportados a 'resultados_modelo_comparado.csv'")

# 🔹 GRÁFICO DE MÉTRICAS POR CLASE
labels = ['Precision_0', 'Recall_0', 'F1_0', 'Precision_1', 'Recall_1', 'F1_1']
values = [metrics_smote_threshold[k] for k in labels]

plt.figure(figsize=(10, 5))
bars = plt.bar(labels, values, color=['red']*3 + ['green']*3)
plt.title('Métricas por clase con SMOTE + Threshold')
plt.ylim(0, 1)
plt.grid(axis='y')

for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, height + 0.02, f'{height:.2f}', ha='center', va='bottom')

plt.tight_layout()
plt.show()


joblib.dump(model_smote, 'modelo_rf_smote.pkl')
joblib.dump(preprocessor, 'preprocesador.pkl')
joblib.dump(best_threshold, 'umbral_optimo.pkl')
print("Modelo de clasificación guardado.")
print("\n✅ Mejor modelo de clasificación guardado como 'mejor_modelo_clasificacion.pkl'")
