import pandas as pd
import os

ruta_raw = 'data/raw/'

# 1. CARGA DE TODOS LOS DATASETS

results = pd.read_csv(os.path.join(ruta_raw, 'results.csv'))
races = pd.read_csv(os.path.join(ruta_raw, 'races.csv'))
drivers = pd.read_csv(os.path.join(ruta_raw, 'drivers.csv'))
constructors = pd.read_csv(os.path.join(ruta_raw, 'constructors.csv'))
status = pd.read_csv(os.path.join(ruta_raw, 'status.csv'))
qualifying = pd.read_csv(os.path.join(ruta_raw, 'qualifying.csv'))
circuits = pd.read_csv(os.path.join(ruta_raw, 'circuits.csv'))
driver_standings = pd.read_csv(os.path.join(ruta_raw, 'driver_standings.csv'))
constructor_standings = pd.read_csv(os.path.join(ruta_raw, 'constructor_standings.csv'))
pit_stops = pd.read_csv(os.path.join(ruta_raw, 'pit_stops.csv'))
seasons = pd.read_csv(os.path.join(ruta_raw, 'seasons.csv'))
constructor_results = pd.read_csv(os.path.join(ruta_raw, 'constructor_results.csv'))
sprint_results = pd.read_csv(os.path.join(ruta_raw, 'sprint_results.csv'))
lap_times = pd.read_csv(os.path.join(ruta_raw, 'lap_times.csv'))

# 2. RENOMBRAR COLUMNAS

races = races.rename(columns={'name': 'race_name'})
drivers = drivers.rename(columns={'nationality': 'driver_nationality'})
constructors = constructors.rename(columns={'name': 'constructor_name', 'nationality': 'constructor_nationality'})
circuits = circuits.rename(columns={'name': 'circuit_name', 'country': 'circuit_country'})
seasons = seasons.rename(columns={'url': 'season_url'})

driver_standings = driver_standings.rename(columns={
    'points': 'driver_season_points', 
    'position': 'driver_season_position',
    'wins': 'driver_season_wins'
})

constructor_standings = constructor_standings.rename(columns={
    'points': 'constructor_season_points', 
    'position': 'constructor_season_position',
    'wins': 'constructor_season_wins'
})

constructor_results = constructor_results.rename(columns={
    'points': 'constructor_race_points',
    'status': 'constructor_race_status'
})

sprint_results = sprint_results.rename(columns={
    'points': 'sprint_points',
    'grid': 'sprint_grid',
    'positionOrder': 'sprint_position',
    'laps': 'sprint_laps'
})

# 3. AGRUPACIONES (Para no multiplicar filas)
# Agrupar paradas en boxes
pit_stops_agrupados = pit_stops.groupby(['raceId', 'driverId']).agg(
    total_pit_stops=('stop', 'max'),
    avg_pit_duration_ms=('milliseconds', 'mean')
).reset_index()

# Agrupar tiempos por vuelta
lap_times_agrupados = lap_times.groupby(['raceId', 'driverId']).agg(
    fastest_lap_ms=('milliseconds', 'min'),
    avg_lap_ms=('milliseconds', 'mean'),
    std_lap_ms=('milliseconds', 'std')
).reset_index()

# 4. MERGE ESTRUCTURADO (Left Joins)

df_unido = results.merge(races[['raceId', 'year', 'round', 'race_name', 'circuitId']], on='raceId', how='left')
df_unido = df_unido.merge(circuits[['circuitId', 'circuit_name', 'circuit_country', 'alt']], on='circuitId', how='left').drop(columns=['circuitId'])
df_unido = df_unido.merge(seasons[['year', 'season_url']], on='year', how='left')
df_unido = df_unido.merge(drivers[['driverId', 'driverRef', 'driver_nationality', 'dob']], on='driverId', how='left')
df_unido = df_unido.merge(constructors[['constructorId', 'constructor_name', 'constructor_nationality']], on='constructorId', how='left')
df_unido = df_unido.merge(status[['statusId', 'status']], on='statusId', how='left')

df_unido = df_unido.merge(qualifying[['raceId', 'driverId', 'position']], on=['raceId', 'driverId'], how='left')
df_unido = df_unido.rename(columns={'position_y': 'quali_position', 'position_x': 'final_position'})

df_unido = df_unido.merge(driver_standings[['raceId', 'driverId', 'driver_season_points', 'driver_season_position', 'driver_season_wins']], on=['raceId', 'driverId'], how='left')
df_unido = df_unido.merge(constructor_standings[['raceId', 'constructorId', 'constructor_season_points', 'constructor_season_position', 'constructor_season_wins']], on=['raceId', 'constructorId'], how='left')

df_unido = df_unido.merge(constructor_results[['raceId', 'constructorId', 'constructor_race_points']], on=['raceId', 'constructorId'], how='left')
df_unido = df_unido.merge(sprint_results[['raceId', 'driverId', 'sprint_points', 'sprint_grid', 'sprint_position', 'sprint_laps']], on=['raceId', 'driverId'], how='left')

# Agregar los datos agrupados
df_unido = df_unido.merge(pit_stops_agrupados, on=['raceId', 'driverId'], how='left')
df_unido = df_unido.merge(lap_times_agrupados, on=['raceId', 'driverId'], how='left')

# 6. EXPORTAR
df_unido.to_csv('data/dataset_f1_unido.csv', index=False)
print(f"Dataset definitivo integrado con éxito. Filas totales: {df_unido.shape[0]}")