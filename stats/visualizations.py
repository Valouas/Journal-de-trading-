"""
stats/visualizations.py - Visualisations graphiques

- Equity Curve (PnL cumulé)
- Calendar Heatmap (PnL par jour)
"""
import pandas as pd
import numpy as np
import calendar
from datetime import datetime


def generate_equity_curve_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Génère les données pour l'equity curve.
    
    Returns:
        DataFrame avec date et PnL cumulé
    """
    if len(df) == 0:
        return pd.DataFrame()
    
    df = df.copy().sort_values('close_time')
    df['cumulative_pnl'] = df['pnl'].cumsum()
    
    return df[['close_time', 'pnl', 'cumulative_pnl', 'symbol', 'direction']].reset_index(drop=True)


def generate_calendar_heatmap_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Génère les données pour le calendar heatmap.
    
    Returns:
        DataFrame avec date, PnL journalier, nb trades
    """
    if len(df) == 0:
        return pd.DataFrame()
    
    df = df.copy()
    df['date'] = df['close_time'].dt.date
    
    daily = df.groupby('date').agg({
        'pnl': 'sum',
        'symbol': 'count',
        'is_win': 'sum'
    }).reset_index()
    
    daily.columns = ['date', 'pnl', 'nb_trades', 'nb_wins']
    daily['winrate'] = (daily['nb_wins'] / daily['nb_trades'] * 100).round(1)
    daily['date'] = pd.to_datetime(daily['date'])
    daily['day'] = daily['date'].dt.day
    daily['month'] = daily['date'].dt.month
    daily['year'] = daily['date'].dt.year
    daily['weekday'] = daily['date'].dt.weekday  # 0=Monday
    daily['week'] = daily['date'].dt.isocalendar().week
    
    return daily


def get_monthly_calendar_matrix(daily_data: pd.DataFrame, year: int, month: int) -> list:
    """
    Génère une matrice calendrier pour un mois donné.
    
    Returns:
        Liste de semaines, chaque semaine est une liste de 7 jours
        Chaque jour est un dict avec {day, pnl, nb_trades} ou None
    """
    month_data = daily_data[
        (daily_data['year'] == year) & (daily_data['month'] == month)
    ].set_index('day').to_dict('index')
    
    cal = calendar.Calendar(firstweekday=0)  # Monday first
    weeks = []
    
    for week in cal.monthdayscalendar(year, month):
        week_data = []
        for day in week:
            if day == 0:
                week_data.append(None)
            else:
                day_info = month_data.get(day, {})
                week_data.append({
                    'day': day,
                    'pnl': day_info.get('pnl', 0),
                    'nb_trades': day_info.get('nb_trades', 0),
                    'winrate': day_info.get('winrate', 0)
                })
        weeks.append(week_data)
    
    return weeks


def get_pnl_color(pnl: float, max_abs_pnl: float) -> str:
    """
    Retourne une couleur CSS basée sur le PnL.
    Vert pour positif, rouge pour négatif, intensité selon montant.
    """
    if pnl == 0:
        return "background-color: #2d2d44;"
    
    # Normaliser l'intensité (0-1)
    intensity = min(abs(pnl) / max_abs_pnl, 1) if max_abs_pnl > 0 else 0.5
    
    if pnl > 0:
        # Vert: plus c'est rentable, plus c'est vert
        green = int(100 + intensity * 155)
        return f"background-color: rgba(46, {green}, 113, {0.3 + intensity * 0.7});"
    else:
        # Rouge: plus c'est en perte, plus c'est rouge
        red = int(100 + intensity * 155)
        return f"background-color: rgba({red}, 76, 60, {0.3 + intensity * 0.7});"


def generate_drawdown_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Génère les données de drawdown pour overlay sur equity curve.
    """
    if len(df) == 0:
        return pd.DataFrame()
    
    df = df.copy().sort_values('close_time')
    df['cumulative_pnl'] = df['pnl'].cumsum()
    df['peak'] = df['cumulative_pnl'].cummax()
    df['drawdown'] = df['cumulative_pnl'] - df['peak']
    
    return df[['close_time', 'drawdown']].reset_index(drop=True)
