import pandas as pd
import joblib
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    make_scorer,
    mean_squared_error,
    mean_absolute_error,
    r2_score
)

df = pd.read_csv('Proyecto/dataset_exito_binario.csv')
features = [
    'LONGITUD_NUM','LATITUD_NUM',
    'ENTORNO_DES','MTS2VENTAS_NUM',
    'NIVELSOCIOECONOMICO_DES','LID_UBICACION_TIENDA', 'exito_binario'
]
df = df.dropna(subset=['Exito'])
X = df[features]
y = df['Exito']

num_feats = ['LONGITUD_NUM','LATITUD_NUM','MTS2VENTAS_NUM', 'exito_binario']
cat_feats = ['ENTORNO_DES','NIVELSOCIOECONOMICO_DES','LID_UBICACION_TIENDA']

preprocessor = ColumnTransformer([
    ('num', StandardScaler(), num_feats),
    ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_feats)
])

pipelines = {
    'SVR': Pipeline([('pp', preprocessor), ('model', SVR())]),
    'RF':  Pipeline([('pp', preprocessor), ('model', RandomForestRegressor(random_state=42))])
}

param_grids = {
    'SVR': {
        'model__kernel': ['rbf','poly'],
        'model__C': [0.1, 1, 10],
        'model__gamma': ['scale','auto']
    },
    'RF': {
        'model__n_estimators': [100, 300],
        'model__max_depth': [None, 10, 30],
        'model__min_samples_leaf': [1, 3, 5]
    }
}

scorers = {
    'R2': make_scorer(r2_score),
    'neg_MSE': make_scorer(mean_squared_error, greater_is_better=False)
}

best_estimators = {}
for name in pipelines:
    grid = GridSearchCV(
        pipelines[name],
        param_grids[name],
        scoring='r2',   
        cv=5,
        n_jobs=-1,
        verbose=1
    )
    grid.fit(X, y)
    best_estimators[name] = grid.best_estimator_
    print(f"\n{name} ➞ Mejores params: {grid.best_params_}")
    print(f"        Mejor R² (CV): {grid.best_score_:.4f}")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, random_state=42, test_size=0.1
)

for name, est in best_estimators.items():
    y_pred = est.predict(X_test)
    r2   = r2_score(y_test, y_pred)
    mae  = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    print(f"\n{name} — R² en test: {r2:.4f},  MAE: {mae:.2f},  RMSE: {rmse:.2f}")


mejor_modelo = max(best_estimators.items(), key=lambda x: x[1].score(X_test, y_test))[1]
joblib.dump(best_estimators['RF'], 'modelo_rf_regresion.pkl')
print("\n✅ Mejor modelo de regresión guardado como 'mejor_modelo_regresion.pkl'")

