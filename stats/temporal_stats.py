"""
stats/temporal_stats.py - Statistiques temporelles

Analyse par:
- Heure (0-23)
- Session (Asie, Europe, US, Overlap)
- Jour de la semaine
"""

import pandas as pd
import numpy as np


def calculate_hourly_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule les statistiques par heure (0-23).
    
    Returns:
        DataFrame avec stats par heure
    """
    if len(df) == 0:
        return pd.DataFrame()
    
    hourly = df.groupby('hour').agg({
        'pnl': ['sum', 'mean', 'count'],
        'is_win': lambda x: (x.sum() / len(x)) * 100 if len(x) > 0 else 0,
        'discipline_score': 'mean'
    }).round(2)
    
    hourly.columns = ['pnl_total', 'pnl_moyen', 'nb_trades', 'winrate', 'discipline_moy']
    
    # Calculer le drawdown par heure
    def calc_hour_dd(hour):
        hour_df = df[df['hour'] == hour]
        if len(hour_df) < 2:
            return 0
        cumsum = hour_df['pnl'].cumsum()
        return (cumsum - cumsum.cummax()).min()
    
    hourly['drawdown'] = [calc_hour_dd(h) for h in hourly.index]
    
    return hourly.reset_index()


def calculate_session_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule les statistiques par session de trading.
    
    Sessions (timezone Suisse):
    - Asie: 01:00-09:00
    - Europe: 09:00-17:00
    - Europe (Overlap): 14:00-17:00
    - US: 17:00-01:00
    """
    if len(df) == 0:
        return pd.DataFrame()
    
    session = df.groupby('session').agg({
        'pnl': ['sum', 'mean', 'count'],
        'is_win': lambda x: (x.sum() / len(x)) * 100 if len(x) > 0 else 0,
        'discipline_score': 'mean',
        'duration_minutes': 'median'
    }).round(2)
    
    session.columns = ['pnl_total', 'pnl_moyen', 'nb_trades', 'winrate', 'discipline_moy', 'duree_mediane']
    
    return session.reset_index()


def calculate_daily_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule les statistiques par jour de la semaine.
    """
    if len(df) == 0:
        return pd.DataFrame()
    
    # Ordre des jours
    day_order = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    
    daily = df.groupby('day_name').agg({
        'pnl': ['sum', 'mean', 'count'],
        'is_win': lambda x: (x.sum() / len(x)) * 100 if len(x) > 0 else 0,
        'discipline_score': 'mean'
    }).round(2)
    
    daily.columns = ['pnl_total', 'pnl_moyen', 'nb_trades', 'winrate', 'discipline_moy']
    daily = daily.reset_index()
    
    # Trier par ordre des jours
    daily['day_order'] = daily['day_name'].apply(lambda x: day_order.index(x) if x in day_order else 7)
    daily = daily.sort_values('day_order').drop('day_order', axis=1)
    
    return daily


def get_toxic_hours(hourly_stats: pd.DataFrame, threshold: float = 0) -> list:
    """
    Identifie les heures avec PnL négatif.
    
    Returns:
        Liste des heures toxiques triées par PnL (pire d'abord)
    """
    if len(hourly_stats) == 0:
        return []
    
    toxic = hourly_stats[hourly_stats['pnl_total'] < threshold]
    return toxic.sort_values('pnl_total')['hour'].tolist()


def get_profitable_hours(hourly_stats: pd.DataFrame, threshold: float = 0) -> list:
    """
    Identifie les heures avec PnL positif.
    
    Returns:
        Liste des heures profitables triées par PnL (meilleure d'abord)
    """
    if len(hourly_stats) == 0:
        return []
    
    profitable = hourly_stats[hourly_stats['pnl_total'] > threshold]
    return profitable.sort_values('pnl_total', ascending=False)['hour'].tolist()


def format_temporal_summary(hourly: pd.DataFrame, sessions: pd.DataFrame, daily: pd.DataFrame) -> str:
    """
    Génère un résumé textuel des patterns temporels.
    """
    lines = []
    
    # Top heures profitables
    if len(hourly) > 0:
        best_hours = hourly.nlargest(3, 'pnl_total')
        worst_hours = hourly.nsmallest(3, 'pnl_total')
        
        lines.append("⏰ HEURES:")
        lines.append(f"  ✅ Meilleures: {', '.join(f'{int(h)}h' for h in best_hours['hour'])}")
        lines.append(f"  🚫 Pires: {', '.join(f'{int(h)}h' for h in worst_hours['hour'])}")
    
    # Sessions
    if len(sessions) > 0:
        best_session = sessions.loc[sessions['pnl_total'].idxmax(), 'session']
        worst_session = sessions.loc[sessions['pnl_total'].idxmin(), 'session']
        lines.append(f"\n🌍 SESSIONS:")
        lines.append(f"  ✅ Meilleure: {best_session}")
        lines.append(f"  🚫 Pire: {worst_session}")
    
    # Jours
    if len(daily) > 0:
        best_day = daily.loc[daily['pnl_total'].idxmax(), 'day_name']
        worst_day = daily.loc[daily['pnl_total'].idxmin(), 'day_name']
        lines.append(f"\n📅 JOURS:")
        lines.append(f"  ✅ Meilleur: {best_day}")
        lines.append(f"  🚫 Pire: {worst_day}")
    
    return "\n".join(lines)
