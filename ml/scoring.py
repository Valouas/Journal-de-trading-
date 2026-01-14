"""
ml/scoring.py - Système de scoring de discipline

Chaque trade commence à 100 points.
Pénalités appliquées selon les comportements détectés.
Score plancher: 0
"""

import pandas as pd
import numpy as np


def calculate_discipline_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule le score de discipline pour chaque trade.
    
    Score initial: 100
    Pénalités:
    - -30 si trade dans les 20% les plus courts (overtrading)
    - -20 si trade après 3+ pertes consécutives (revenge trading)
    - -10 si trade pris <5min après le précédent (impulsivité)
    
    Args:
        df: DataFrame avec les trades normalisés
    
    Returns:
        DataFrame avec colonne 'discipline_score' ajoutée
    """
    df = df.copy()
    
    # Score initial
    df['discipline_score'] = 100
    
    # --- Pénalité 1: Trade trop court (bottom 20%) ---
    if len(df) > 5:  # Minimum de trades pour calculer le percentile
        duration_20th = df['duration_minutes'].quantile(0.20)
        mask_short = df['duration_minutes'] <= duration_20th
        df.loc[mask_short, 'discipline_score'] -= 30
    
    # --- Pénalité 2: Trade après séquence de pertes ---
    # Calculer le nombre de pertes consécutives avant chaque trade
    df['prev_loss_streak'] = 0
    loss_streak = 0
    streaks = []
    
    for idx, row in df.iterrows():
        streaks.append(loss_streak)
        if not row['is_win']:
            loss_streak += 1
        else:
            loss_streak = 0
    
    df['prev_loss_streak'] = streaks
    # Pénalité revenge trading (après 5+ pertes consécutives)
    mask_revenge = df['prev_loss_streak'] >= 5
    df.loc[mask_revenge, 'discipline_score'] -= 20
    
    # --- Pénalité 3: Trade trop rapide après le précédent ---
    df['time_since_prev'] = df['open_time'].diff().dt.total_seconds() / 60
    mask_impulse = df['time_since_prev'] < 5
    df.loc[mask_impulse, 'discipline_score'] -= 10
    
    # Score plancher à 0
    df['discipline_score'] = df['discipline_score'].clip(lower=0)
    
    return df


def label_trades(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ajoute des labels aux trades selon leur score et résultat.
    
    Labels:
    - 'Trade destructeur': score < 40
    - 'Faux bon trade': gagnant mais score < 60
    - 'Trade sain': autres
    
    Args:
        df: DataFrame avec discipline_score
    
    Returns:
        DataFrame avec colonne 'trade_label' ajoutée
    """
    df = df.copy()
    
    conditions = [
        df['discipline_score'] < 40,
        (df['is_win']) & (df['discipline_score'] < 60),
    ]
    choices = ['Trade destructeur', 'Faux bon trade']
    
    df['trade_label'] = np.select(conditions, choices, default='Trade sain')
    
    # Flags booléens pour faciliter le filtrage
    df['is_destructive'] = df['discipline_score'] < 40
    df['is_false_good'] = (df['is_win']) & (df['discipline_score'] < 60)
    
    return df


def get_discipline_summary(df: pd.DataFrame) -> dict:
    """
    Calcule les statistiques globales de discipline.
    
    Returns:
        Dict avec les métriques de discipline
    """
    return {
        'avg_score': df['discipline_score'].mean(),
        'median_score': df['discipline_score'].median(),
        'min_score': df['discipline_score'].min(),
        'max_score': df['discipline_score'].max(),
        'pct_destructive': (df['is_destructive'].sum() / len(df)) * 100,
        'pct_false_good': (df['is_false_good'].sum() / len(df)) * 100,
        'pct_healthy': ((~df['is_destructive'] & ~df['is_false_good']).sum() / len(df)) * 100,
        'total_trades': len(df),
        'destructive_count': df['is_destructive'].sum(),
        'false_good_count': df['is_false_good'].sum()
    }
