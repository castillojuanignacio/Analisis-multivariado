import pandas as pd
import numpy as np
from sklearn.preprocessing import RobustScaler

# Cargar dataset
df = pd.read_csv('data/dataset_f1_unido.csv', low_memory=False)

# 2. ELIMINAR COLUMNAS INNECESARIAS / CON EXCESO DE NULOS
columnas_a_eliminar = [
    # IDs y variables de contexto
    'resultId', 'driverId', 'constructorId', 'statusId', 'year', 'round',
    # Columnas de Sprint
    'sprint_points', 'sprint_laps', 'sprint_grid', 'sprint_position',
    # Métricas de tiempo y ranking con demasiados nulos
    'avg_pit_duration_ms', 'fastest_lap_ms', 'avg_lap_ms', 'std_lap_ms',
    'milliseconds', 'fastestLap', 'fastestLapTime', 'fastestLapSpeed', 'fastest_lap_rank',
    # Columnas que no aportan valor o que ya transformamos
    'alt', 'laps'

    'driver_season_points', 'driver_season_wins', # Evita sesgo histórico vs carrera actual
    'constructor_season_points', 'constructor_season_wins',
    'constructor_season_position', 'driver_season_position'
]
df = df.drop(columns=columnas_a_eliminar, errors='ignore')

# 3. IMPUTACIÓN CON SENTIDO LÓGICO
# Rellenar con 0 
cols_ceros = [
    'driver_season_points', 'driver_season_wins', 
    'constructor_season_points', 'constructor_season_wins', 
    'constructor_race_points', 'total_pit_stops'
]
for col in cols_ceros:
    if col in df.columns:
        df[col] = df[col].fillna(0)

# Rellenar posiciones con el máximo de la carrera (peor posición)
cols_posiciones = [
    'quali_position', 'driver_season_position', 'constructor_season_position'
]
for col in cols_posiciones:
    if col in df.columns:
        df[col] = df.groupby('raceId')[col].transform(lambda x: x.fillna(x.max()))
        df[col] = df[col].fillna(22)

# Se elimina raceId porque ya no se necesita para agrupar
df = df.drop(columns=['raceId'], errors='ignore')

# 4. FILTRADO DE NUMÉRICAS Y NULOS RESTANTES
df_numeric = df.select_dtypes(include=['number'])
df_numeric = df_numeric.dropna()

# 5. ELIMINACIÓN DE VARIABLES ALTAMENTE CORRELACIONADAS
# Esto evita que el PCA sobredimensione características que miden lo mismo (ej. puntos y posición)
corr_matrix = df_numeric.corr().abs()
# Seleccionamos el triángulo superior de la matriz de correlación
upper_tri = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
# Identificamos columnas con correlación mayor a 0.90
cols_to_drop_corr = [column for column in upper_tri.columns if any(upper_tri[column] > 0.90)]
df_numeric = df_numeric.drop(columns=cols_to_drop_corr)

print(f"Columnas eliminadas por redundancia (correlación > 0.90): {cols_to_drop_corr}")

# 6. ESTANDARIZACIÓN ROBUSTA (Manejo de Outliers)
# RobustScaler usa la mediana y el rango intercuartílico, ideal para las anomalías de la F1
scaler = RobustScaler()
df_scaled_array = scaler.fit_transform(df_numeric)

df_scaled = pd.DataFrame(df_scaled_array, columns=df_numeric.columns, index=df_numeric.index)

# 7. GUARDADO
df_scaled.to_csv('data/dataset_f1_estandarizado.csv', index=False)

print("Preprocesamiento definitivo finalizado y guardado.")