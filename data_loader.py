"""
data_loader.py - Chargement et normalisation des données MEXC Futures

Ce module gère:
- Le chargement des fichiers CSV/XLSX MEXC
- La normalisation des colonnes
- Le calcul des métriques dérivées (durée, session, heure)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Tuple, Optional


def load_file(file) -> pd.DataFrame:
    """
    Charge un fichier CSV ou XLSX uploadé via Streamlit.
    
    Args:
        file: Fichier uploadé (UploadedFile de Streamlit)
    
    Returns:
        DataFrame pandas avec les données brutes
    """
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    elif file.name.endswith(('.xlsx', '.xls')):
        return pd.read_excel(file)
    else:
        raise ValueError(f"Format non supporté: {file.name}. Utilisez CSV ou XLSX.")


def get_session(hour: int) -> str:
    """
    Détermine la session de trading selon l'heure (timezone Suisse).
    
    Sessions:
    - Asie: 01:00-09:00 (CH)
    - Europe: 09:00-17:00 (CH)
    - US: 17:00-01:00 (CH)
    - Overlap: 14:00-17:00 (inclus dans Europe/US)
    
    Args:
        hour: Heure (0-23) en timezone Suisse
    
    Returns:
        Nom de la session
    """
    if 1 <= hour < 9:
        return "Asie"
    elif 9 <= hour < 17:
        if 14 <= hour < 17:
            return "Europe (Overlap)"
        return "Europe"
    else:
        return "US"


def get_day_name(day_num: int) -> str:
    """Convertit le numéro du jour en nom français."""
    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    return days[day_num]


def normalize_positions(df_positions: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise le fichier d'historique des positions MEXC.
    
    Colonnes attendues:
    - Futures, Open Time, Close Time, Direction
    - Avg Entry Price, Avg Close Price
    - Closing Qty (Cont.), Trading Fee, Realized PNL
    
    Returns:
        DataFrame normalisé avec colonnes standardisées
    """
    df = df_positions.copy()
    
    # Mapping des colonnes MEXC -> colonnes normalisées
    column_mapping = {
        'Futures': 'symbol',
        'Open Time': 'open_time',
        'Close Time': 'close_time',
        'Direction': 'direction',
        'Avg Entry Price': 'entry_price',
        'Avg Close Price': 'exit_price',
        'Closing Qty (Cont.)': 'quantity',
        'Trading Fee': 'fees',
        'Realized PNL': 'pnl',
        'Status': 'status',
        'UID': 'uid'
    }
    
    # Renommer les colonnes existantes
    df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
    
    # Convertir les dates
    df['open_time'] = pd.to_datetime(df['open_time'])
    df['close_time'] = pd.to_datetime(df['close_time'])
    
    # Calculer la durée en minutes
    df['duration_minutes'] = (df['close_time'] - df['open_time']).dt.total_seconds() / 60
    
    # Extraire l'heure (0-23) basée sur close_time
    df['hour'] = df['close_time'].dt.hour
    
    # Extraire le jour de la semaine (0=Lundi, 6=Dimanche)
    df['day_of_week'] = df['close_time'].dt.dayofweek
    df['day_name'] = df['day_of_week'].apply(get_day_name)
    
    # Déterminer la session
    df['session'] = df['hour'].apply(get_session)
    
    # Normaliser la direction
    df['direction'] = df['direction'].str.upper().str.strip()
    df['direction'] = df['direction'].replace({
        'OPEN LONG': 'LONG',
        'OPEN SHORT': 'SHORT',
        'CLOSE LONG': 'LONG',
        'CLOSE SHORT': 'SHORT'
    })
    
    # S'assurer que pnl est numérique (enlever le suffixe USDT si présent)
    def clean_numeric(val):
        if pd.isna(val):
            return 0
        val_str = str(val).upper().replace('USDT', '').replace(',', '.').strip()
        try:
            return float(val_str)
        except:
            return 0
    
    df['pnl'] = df['pnl'].apply(clean_numeric)
    df['fees'] = df['fees'].apply(clean_numeric)
    
    # Calculer PnL brut (avant fees)
    df['pnl_gross'] = df['pnl'] + abs(df['fees'])
    
    # Flag trade gagnant
    df['is_win'] = df['pnl'] > 0
    
    return df


def enrich_with_orders(df_positions: pd.DataFrame, df_orders: pd.DataFrame) -> pd.DataFrame:
    """
    Enrichit les positions avec les données des ordres (levier, type d'ordre).
    
    Args:
        df_positions: DataFrame des positions normalisées
        df_orders: DataFrame brut des ordres MEXC
    
    Returns:
        DataFrame enrichi avec levier et type d'ordre
    """
    df = df_positions.copy()
    
    # Extraire les informations de levier des ordres
    if 'Effet de levier' in df_orders.columns:
        # Créer un mapping symbol -> levier moyen
        orders_copy = df_orders.copy()
        orders_copy['symbol'] = orders_copy.get('Paire de contrats à terme', 
                                                 orders_copy.get('Futures', '')).str.strip()
        
        # Extraire le levier numérique (ex: "50x" -> 50)
        orders_copy['leverage'] = orders_copy['Effet de levier'].astype(str).str.extract(r'(\d+)').astype(float)
        
        # Calculer le levier moyen par symbol
        leverage_by_symbol = orders_copy.groupby('symbol')['leverage'].mean().to_dict()
        
        # Appliquer aux positions
        df['leverage'] = df['symbol'].map(leverage_by_symbol).fillna(1)
    else:
        df['leverage'] = 1
    
    # Extraire le type d'ordre
    if "Type d'ordre" in df_orders.columns:
        # Compter le type d'ordre dominant par symbol
        orders_copy = df_orders.copy()
        orders_copy['symbol'] = orders_copy.get('Paire de contrats à terme',
                                                 orders_copy.get('Futures', '')).str.strip()
        orders_copy['order_type'] = orders_copy["Type d'ordre"].str.upper()
        
        # Mapper MARKET ou LIMIT
        def classify_order_type(order_type):
            if pd.isna(order_type):
                return 'UNKNOWN'
            order_type = str(order_type).upper()
            if 'MARKET' in order_type:
                return 'MARKET'
            elif 'LIMIT' in order_type:
                return 'LIMIT'
            return 'OTHER'
        
        orders_copy['order_type_clean'] = orders_copy['order_type'].apply(classify_order_type)
        
        # On ne peut pas directement mapper les ordres aux positions
        # On met un placeholder pour l'instant
        df['order_type'] = 'UNKNOWN'
    else:
        df['order_type'] = 'UNKNOWN'
    
    return df


def normalize_data(positions_file, orders_file) -> pd.DataFrame:
    """
    Point d'entrée principal: charge et normalise les deux fichiers MEXC.
    
    Args:
        positions_file: Fichier d'historique des positions
        orders_file: Fichier d'historique des ordres
    
    Returns:
        DataFrame normalisé et enrichi prêt pour l'analyse
    """
    # Charger les fichiers
    df_positions = load_file(positions_file)
    df_orders = load_file(orders_file)
    
    # Normaliser les positions
    df = normalize_positions(df_positions)
    
    # Enrichir avec les ordres
    df = enrich_with_orders(df, df_orders)
    
    # Trier par date de clôture
    df = df.sort_values('close_time').reset_index(drop=True)
    
    return df


def get_leverage_from_orders(orders_file) -> dict:
    """
    Extrait le levier par trade depuis le fichier d'ordres.
    
    Returns:
        Dict avec symbol -> leverage moyen
    """
    df = load_file(orders_file)
    
    if 'Effet de levier' not in df.columns:
        return {}
    
    df['symbol'] = df.get('Paire de contrats à terme', df.get('Futures', '')).str.strip()
    df['leverage'] = df['Effet de levier'].astype(str).str.extract(r'(\d+)').astype(float)
    
    return df.groupby('symbol')['leverage'].mean().to_dict()
