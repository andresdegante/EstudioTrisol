import pandas as pd
import numpy as np
import ast
import warnings

# --- CONFIGURACIÓN ---
INPUT_CSV = 'TMDB_movie_dataset_v11.csv'
OUTPUT_CSV = 'datos_limpios_peliculas.csv'

# Suprimir advertencias
warnings.filterwarnings('ignore', category=UserWarning, module='pandas')

# --- Funciones de Parseo ---
def safe_parse_json(data_str):
    try:
        return ast.literal_eval(data_str)
    except (ValueError, SyntaxError, TypeError):
        return []

def get_first_genre(genres_list):
    try:
        if isinstance(genres_list, list) and len(genres_list) > 0:
            if isinstance(genres_list[0], dict):
                 return genres_list[0]['name']
    except Exception:
        pass
    return 'Unknown'

def parse_genres_robust(data):
    if isinstance(data, str):
        if data.startswith('['):
            return safe_parse_json(data)
        else:
            return [{'name': g.strip()} for g in data.split(',')]
    return []

print("--- Iniciando la transformación del dataset ---")

try:
    # --- Carga ---
    df = pd.read_csv(INPUT_CSV)
    print(f"[1/4] Archivo original '{INPUT_CSV}' cargado ({len(df)} filas).")

    # --- Transformación ---
    df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce')
    df['budget'] = pd.to_numeric(df['budget'], errors='coerce')
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    print("[2/4] Columnas clave transformadas a formato numérico y de fecha.")

    # --- Limpieza ---
    df = df.dropna(subset=['revenue', 'budget', 'release_date', 'genres'])
    df_clean = df[(df['revenue'] > 1000) & (df['budget'] > 1000)].copy()
    
    if df_clean.empty:
        raise ValueError("No se encontraron filas con datos financieros válidos (revenue > 1000 y budget > 1000).")

    print(f"[3/4] Filas con datos financieros inválidos eliminadas. Quedan {len(df_clean)} filas.")

    # --- Ingeniería de Características ---
    df_clean['roi'] = (df_clean['revenue'] - df_clean['budget']) / df_clean['budget']
    df_clean['genres_list'] = df_clean['genres'].apply(parse_genres_robust)
    df_clean['main_genre'] = df_clean['genres_list'].apply(get_first_genre)
    df_clean['release_year'] = df_clean['release_date'].dt.year
    
    # --- Selección y Limpieza Final ---
    cols_to_keep = [
        'title', 'revenue', 'budget', 'roi', 'main_genre', 
        'release_year', 'runtime', 'vote_average'
    ]
    df_final = df_clean[cols_to_keep].copy()
    df_final = df_final.dropna()
    df_final = df_final[df_final['main_genre'] != 'Unknown']
    df_final['release_year'] = df_final['release_year'].astype(int)
    
    # --- Guardado ---
    df_final.to_csv(OUTPUT_CSV, index=False)
    
    print(f"[4/4] Limpieza final completada.")
    print("\n--- ¡ÉXITO! ---")
    print(f"Se ha creado el archivo '{OUTPUT_CSV}' con {len(df_final)} filas limpias y listas para usar.")
    print("Este es el único CSV que necesitas subir a GitHub con tu app.")

except FileNotFoundError:
    print(f"Error: No se encontró el archivo '{INPUT_CSV}'. Asegúrate de que esté en la misma carpeta.")
except Exception as e:
    print(f"Ocurrió un error: {e}")
