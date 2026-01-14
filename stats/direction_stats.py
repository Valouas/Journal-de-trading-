"""
stats/direction_stats.py - Statistiques par direction (LONG / SHORT)

Analyse séparée des performances LONG et SHORT.
"""

import pandas as pd
import numpy as np


def calculate_direction_stats(df: pd.DataFrame) -> dict:
    """
    Calcule les statistiques séparées pour LONG et SHORT.
    
    Returns:
        Dict avec stats LONG et SHORT
    """
    results = {}
    
    for direction in ['LONG', 'SHORT']:
        dir_df = df[df['direction'] == direction]
        
        if len(dir_df) == 0:
            results[direction.lower()] = {
                'count': 0,
                'pnl_total': 0,
                'winrate': 0,
                'avg_pnl': 0,
                'avg_rr': 0,
                'max_drawdown': 0,
                'max_win_streak': 0,
                'max_loss_streak': 0
            }
            continue
        
        # Stats de base
        pnl_total = dir_df['pnl'].sum()
        nb_wins = (dir_df['pnl'] > 0).sum()
        nb_losses = (dir_df['pnl'] < 0).sum()
        winrate = (nb_wins / len(dir_df)) * 100
        
        # R:R moyen
        avg_win = dir_df[dir_df['pnl'] > 0]['pnl'].mean() if nb_wins > 0 else 0
        avg_loss = abs(dir_df[dir_df['pnl'] < 0]['pnl'].mean()) if nb_losses > 0 else 0
        avg_rr = avg_win / avg_loss if avg_loss > 0 else 0
        
        # Drawdown
        cumulative = dir_df['pnl'].cumsum()
        max_dd = (cumulative - cumulative.cummax()).min()
        
        # Séquences
        win_streak, loss_streak = calculate_streaks(dir_df['pnl'])
        
        results[direction.lower()] = {
            'count': len(dir_df),
            'pnl_total': round(pnl_total, 2),
            'winrate': round(winrate, 1),
            'avg_pnl': round(dir_df['pnl'].mean(), 2),
            'avg_rr': round(avg_rr, 2),
            'max_drawdown': round(max_dd, 2),
            'max_win_streak': win_streak,
            'max_loss_streak': loss_streak,
            'nb_wins': int(nb_wins),
            'nb_losses': int(nb_losses)
        }
    
    return results


def calculate_streaks(pnl_series: pd.Series) -> tuple:
    """
    Calcule les séquences max de gains et pertes.
    
    Returns:
        (max_win_streak, max_loss_streak)
    """
    if len(pnl_series) == 0:
        return 0, 0
    
    wins = (pnl_series > 0).astype(int)
    losses = (pnl_series < 0).astype(int)
    
    # Calculer les séquences
    max_win = max_loss = 0
    current_win = current_loss = 0
    
    for w, l in zip(wins, losses):
        if w:
            current_win += 1
            current_loss = 0
            max_win = max(max_win, current_win)
        elif l:
            current_loss += 1
            current_win = 0
            max_loss = max(max_loss, current_loss)
        else:
            current_win = current_loss = 0
    
    return max_win, max_loss


def format_direction_comparison(stats: dict) -> pd.DataFrame:
    """
    Crée un DataFrame comparatif LONG vs SHORT.
    """
    long = stats.get('long', {})
    short = stats.get('short', {})
    
    data = {
        'Métrique': [
            'Nombre de trades',
            'PnL Total ($)',
            'Win Rate (%)',
            'PnL Moyen ($)',
            'R:R Moyen',
            'Drawdown Max ($)',
            'Série wins max',
            'Série pertes max'
        ],
        'LONG': [
            long.get('count', 0),
            long.get('pnl_total', 0),
            long.get('winrate', 0),
            long.get('avg_pnl', 0),
            long.get('avg_rr', 0),
            long.get('max_drawdown', 0),
            long.get('max_win_streak', 0),
            long.get('max_loss_streak', 0)
        ],
        'SHORT': [
            short.get('count', 0),
            short.get('pnl_total', 0),
            short.get('winrate', 0),
            short.get('avg_pnl', 0),
            short.get('avg_rr', 0),
            short.get('max_drawdown', 0),
            short.get('max_win_streak', 0),
            short.get('max_loss_streak', 0)
        ]
    }
    
    return pd.DataFrame(data)
