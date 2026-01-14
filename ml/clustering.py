"""
ml/clustering.py - Clustering comportemental KMeans

Groupe les trades en 3 clusters basés sur:
- duration_minutes
- hour
- pnl
- discipline_score
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


def perform_clustering(df: pd.DataFrame, n_clusters: int = 3) -> pd.DataFrame:
    """
    Applique un clustering KMeans sur les trades.
    
    Features utilisées:
    - duration_minutes: durée du trade
    - hour: heure de clôture
    - pnl: profit/perte
    - discipline_score: score de discipline
    
    Args:
        df: DataFrame avec les trades
        n_clusters: Nombre de clusters (défaut: 3)
    
    Returns:
        DataFrame avec colonne 'cluster' ajoutée
    """
    df = df.copy()
    
    # Features pour le clustering
    features = ['duration_minutes', 'hour', 'pnl', 'discipline_score']
    
    # Vérifier que toutes les features existent
    missing = [f for f in features if f not in df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes: {missing}")
    
    # Préparer les données
    X = df[features].copy()
    
    # Gérer les valeurs manquantes
    X = X.fillna(X.median())
    
    # Normaliser les features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Appliquer KMeans
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df['cluster'] = kmeans.fit_predict(X_scaled)
    
    return df


def get_cluster_profiles(df: pd.DataFrame) -> pd.DataFrame:
    """
    Génère un profil descriptif pour chaque cluster.
    
    Returns:
        DataFrame avec les statistiques par cluster
    """
    profiles = df.groupby('cluster').agg({
        'pnl': ['sum', 'mean', 'count'],
        'duration_minutes': ['median', 'mean'],
        'hour': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else x.median(),
        'discipline_score': 'mean',
        'is_win': lambda x: (x.sum() / len(x)) * 100,
        'direction': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'MIXED'
    }).round(2)
    
    # Aplatir les colonnes multi-index
    profiles.columns = [
        'pnl_total', 'pnl_moyen', 'nb_trades',
        'duree_mediane_min', 'duree_moyenne_min',
        'heure_dominante',
        'discipline_moyenne',
        'winrate_pct',
        'direction_dominante'
    ]
    
    # Ajouter un label descriptif
    def get_cluster_label(row):
        if row['pnl_total'] > 0 and row['discipline_moyenne'] > 70:
            return "🟢 Comportement optimal"
        elif row['pnl_total'] < 0 and row['discipline_moyenne'] < 50:
            return "🔴 Comportement destructeur"
        elif row['duree_mediane_min'] < 10:
            return "🟡 Scalping rapide"
        else:
            return "🟠 Comportement mixte"
    
    profiles['label'] = profiles.apply(get_cluster_label, axis=1)
    
    return profiles.reset_index()


def get_cluster_summary(df: pd.DataFrame) -> list:
    """
    Génère un résumé textuel de chaque cluster.
    
    Returns:
        Liste de descriptions textuelles
    """
    profiles = get_cluster_profiles(df)
    summaries = []
    
    for _, row in profiles.iterrows():
        summary = {
            'cluster': int(row['cluster']),
            'label': row['label'],
            'description': (
                f"Cluster {int(row['cluster'])}: {row['nb_trades']} trades, "
                f"PnL total: {row['pnl_total']:.2f}$, "
                f"Durée médiane: {row['duree_mediane_min']:.1f}min, "
                f"Heure dominante: {int(row['heure_dominante'])}h, "
                f"Win rate: {row['winrate_pct']:.1f}%, "
                f"Discipline: {row['discipline_moyenne']:.1f}/100"
            ),
            'pnl_total': row['pnl_total'],
            'nb_trades': row['nb_trades'],
            'winrate': row['winrate_pct'],
            'discipline': row['discipline_moyenne']
        }
        summaries.append(summary)
    
    return summaries
