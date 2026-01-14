"""
stats/asset_stats.py - Statistiques par actif (paire)

Analyse par crypto/paire tradée.
"""

import pandas as pd
import numpy as np


def calculate_asset_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule les statistiques par actif/paire.
    
    Returns:
        DataFrame avec stats par symbol, trié par PnL total
    """
    if len(df) == 0:
        return pd.DataFrame()
    
    assets = df.groupby('symbol').agg({
        'pnl': ['sum', 'mean', 'count'],
        'is_win': lambda x: (x.sum() / len(x)) * 100 if len(x) > 0 else 0,
        'discipline_score': 'mean',
        'is_destructive': lambda x: (x.sum() / len(x)) * 100 if len(x) > 0 else 0,
        'duration_minutes': 'median',
        'fees': lambda x: abs(x).sum()
    }).round(2)
    
    assets.columns = [
        'pnl_total', 'pnl_moyen', 'nb_trades',
        'winrate', 'discipline_moy', 'pct_destructeurs',
        'duree_mediane', 'fees_total'
    ]
    
    # Trier par PnL total (meilleur en premier)
    assets = assets.sort_values('pnl_total', ascending=False)
    
    return assets.reset_index()


def get_toxic_assets(asset_stats: pd.DataFrame) -> pd.DataFrame:
    """
    Identifie les actifs avec PnL négatif.
    """
    if len(asset_stats) == 0:
        return pd.DataFrame()
    
    return asset_stats[asset_stats['pnl_total'] < 0].sort_values('pnl_total')


def get_profitable_assets(asset_stats: pd.DataFrame) -> pd.DataFrame:
    """
    Identifie les actifs avec PnL positif.
    """
    if len(asset_stats) == 0:
        return pd.DataFrame()
    
    return asset_stats[asset_stats['pnl_total'] > 0].sort_values('pnl_total', ascending=False)


def calculate_cross_analysis(df: pd.DataFrame) -> dict:
    """
    Calcule les analyses croisées:
    - Actif × Heure
    - Direction × Heure
    - Actif × Direction
    
    Returns:
        Dict avec les DataFrames d'analyse croisée
    """
    result = {}
    
    # Actif × Heure
    if 'symbol' in df.columns and 'hour' in df.columns:
        cross_asset_hour = df.pivot_table(
            values='pnl',
            index='symbol',
            columns='hour',
            aggfunc='sum',
            fill_value=0
        ).round(2)
        result['asset_hour'] = cross_asset_hour
    
    # Direction × Heure
    if 'direction' in df.columns and 'hour' in df.columns:
        cross_dir_hour = df.pivot_table(
            values='pnl',
            index='direction',
            columns='hour',
            aggfunc='sum',
            fill_value=0
        ).round(2)
        result['direction_hour'] = cross_dir_hour
    
    # Actif × Direction
    if 'symbol' in df.columns and 'direction' in df.columns:
        cross_asset_dir = df.pivot_table(
            values='pnl',
            index='symbol',
            columns='direction',
            aggfunc='sum',
            fill_value=0
        ).round(2)
        result['asset_direction'] = cross_asset_dir
    
    return result


def format_asset_summary(asset_stats: pd.DataFrame) -> str:
    """
    Génère un résumé textuel des actifs.
    """
    if len(asset_stats) == 0:
        return "Aucun actif à analyser"
    
    lines = ["🪙 CLASSEMENT DES ACTIFS:", ""]
    
    for i, row in asset_stats.head(10).iterrows():
        emoji = "🟢" if row['pnl_total'] > 0 else "🔴"
        lines.append(
            f"{emoji} {row['symbol']}: {row['pnl_total']}$ "
            f"({row['nb_trades']} trades, WR: {row['winrate']}%, "
            f"Discipline: {row['discipline_moy']:.0f})"
        )
    
    return "\n".join(lines)
