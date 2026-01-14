"""
stats/trade_types.py - Classification et analyse des types de trades

Types de trades:
- SCALP: Durée < 5 min
- SWING: Durée > 60 min  
- HIGH_LEV: Levier >= 50x (home run)
- STANDARD: Autres trades
"""
import pandas as pd
import numpy as np


def classify_trade_type(duration_min: float, leverage: float) -> str:
    """
    Classifie un trade selon sa durée et son levier.
    
    Args:
        duration_min: Durée en minutes
        leverage: Levier utilisé
    
    Returns:
        Type de trade: 'scalp', 'swing', 'high_lev', ou 'standard'
    """
    # High leverage prend la priorité (home run attempt)
    if leverage >= 50:
        return 'high_lev'
    
    # Ensuite basé sur la durée
    if duration_min < 5:
        return 'scalp'
    elif duration_min > 60:
        return 'swing'
    else:
        return 'standard'


def add_trade_type_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ajoute une colonne 'trade_type' au DataFrame.
    """
    df = df.copy()
    df['trade_type'] = df.apply(
        lambda row: classify_trade_type(
            row.get('duration_minutes', 0),
            row.get('leverage', 1)
        ),
        axis=1
    )
    return df


def calculate_trade_type_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule les statistiques par type de trade.
    
    Returns:
        DataFrame avec stats par type (comme dans l'image)
    """
    if 'trade_type' not in df.columns:
        df = add_trade_type_column(df)
    
    stats = []
    for trade_type in ['swing', 'scalp', 'high_lev', 'standard']:
        subset = df[df['trade_type'] == trade_type]
        if len(subset) == 0:
            continue
            
        wins = subset[subset['pnl'] > 0]
        losses = subset[subset['pnl'] < 0]
        
        total_gains = wins['pnl'].sum() if len(wins) > 0 else 0
        total_losses = abs(losses['pnl'].sum()) if len(losses) > 0 else 0
        
        stats.append({
            'Setup': trade_type.upper(),
            'Nb trades': len(subset),
            'PnL net ($)': round(subset['pnl'].sum(), 2),
            'PnL brut ($)': round(subset['pnl_gross'].sum(), 2) if 'pnl_gross' in subset.columns else 0,
            'Fees ($)': round(subset['fees'].sum(), 2) if 'fees' in subset.columns else 0,
            'Winrate (%)': round(len(wins) / len(subset) * 100, 1) if len(subset) > 0 else 0,
            'Avg win ($)': round(wins['pnl'].mean(), 2) if len(wins) > 0 else 0,
            'Avg loss ($)': round(losses['pnl'].mean(), 2) if len(losses) > 0 else 0,
            'Profit Factor': round(total_gains / total_losses, 2) if total_losses > 0 else float('inf'),
            'Durée méd (min)': round(subset['duration_minutes'].median(), 1),
            'Max DD ($)': round(calculate_max_drawdown(subset), 2)
        })
    
    return pd.DataFrame(stats)


def calculate_trade_type_by_direction(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule les statistiques par type de trade ET direction.
    """
    if 'trade_type' not in df.columns:
        df = add_trade_type_column(df)
    
    stats = []
    for trade_type in ['swing', 'scalp', 'high_lev', 'standard']:
        for direction in ['LONG', 'SHORT']:
            subset = df[(df['trade_type'] == trade_type) & (df['direction'] == direction)]
            if len(subset) == 0:
                continue
                
            wins = subset[subset['pnl'] > 0]
            losses = subset[subset['pnl'] < 0]
            
            total_gains = wins['pnl'].sum() if len(wins) > 0 else 0
            total_losses = abs(losses['pnl'].sum()) if len(losses) > 0 else 0
            
            stats.append({
                'Setup': trade_type.upper(),
                'Direction': direction,
                'Nb trades': len(subset),
                'PnL net ($)': round(subset['pnl'].sum(), 2),
                'Winrate (%)': round(len(wins) / len(subset) * 100, 1) if len(subset) > 0 else 0,
                'Avg win ($)': round(wins['pnl'].mean(), 2) if len(wins) > 0 else 0,
                'Avg loss ($)': round(losses['pnl'].mean(), 2) if len(losses) > 0 else 0,
                'Profit Factor': round(total_gains / total_losses, 2) if total_losses > 0 else 0,
                'Durée méd (min)': round(subset['duration_minutes'].median(), 1)
            })
    
    return pd.DataFrame(stats)


def calculate_max_drawdown(df: pd.DataFrame) -> float:
    """Calcule le max drawdown d'un subset de trades."""
    if len(df) == 0:
        return 0
    cumsum = df['pnl'].cumsum()
    peak = cumsum.cummax()
    dd = cumsum - peak
    return dd.min()


def calculate_tiltmeter(df: pd.DataFrame) -> dict:
    """
    Calcule le Tiltmeter - score émotionnel basé sur les patterns comportementaux.
    
    Score de 0-100:
    - 100 = Trading parfaitement discipliné
    - 0 = En plein tilt
    
    Facteurs négatifs:
    - Revenge trading (trades après pertes)
    - Overtrading (trop de trades en peu de temps)
    - Trades impulsifs (< 5 min après le précédent)
    - Trades en dehors des heures optimales
    """
    if len(df) == 0:
        return {'score': 100, 'status': 'neutral', 'alerts': []}
    
    score = 100
    alerts = []
    
    # Calculer les métriques de tilt
    df_sorted = df.sort_values('close_time').copy()
    
    # 1. Revenge trading - trades après 5+ pertes consécutives
    # Calculer les séries de pertes
    df_sorted['is_loss'] = df_sorted['pnl'] < 0
    df_sorted['loss_streak'] = df_sorted['is_loss'].groupby(
        (~df_sorted['is_loss']).cumsum()
    ).cumsum()
    df_sorted['prev_loss_streak'] = df_sorted['loss_streak'].shift(1).fillna(0)
    
    # Revenge = trade après 5+ pertes consécutives
    revenge_trades = df_sorted[df_sorted['prev_loss_streak'] >= 5]
    revenge_pct = len(revenge_trades) / len(df) * 100 if len(df) > 0 else 0
    if revenge_pct > 20:
        score -= 25
        alerts.append("🔥 Revenge trading détecté")
    elif revenge_pct > 10:
        score -= 15
        alerts.append("⚠️ Tendance au revenge trading")
    
    # 2. Overtrading - plus de 10 trades par jour en moyenne
    df_sorted['date'] = df_sorted['close_time'].dt.date
    trades_per_day = df_sorted.groupby('date').size()
    avg_trades = trades_per_day.mean()
    if avg_trades > 15:
        score -= 20
        alerts.append("🚨 Overtrading sévère")
    elif avg_trades > 10:
        score -= 10
        alerts.append("⚠️ Tendance à l'overtrading")
    
    # 3. Trades impulsifs - moins de 5 min après le précédent
    df_sorted['time_since_prev'] = (
        df_sorted['close_time'] - df_sorted['close_time'].shift(1)
    ).dt.total_seconds() / 60
    impulsive = df_sorted[df_sorted['time_since_prev'] < 5]
    impulsive_pct = len(impulsive) / len(df) * 100 if len(df) > 0 else 0
    if impulsive_pct > 30:
        score -= 20
        alerts.append("💨 Trop de trades impulsifs")
    elif impulsive_pct > 15:
        score -= 10
        alerts.append("⚡ Trades impulsifs fréquents")
    
    # 4. Trades perdants récents (derniers 5 trades)
    last_trades = df_sorted.tail(5)
    recent_losses = (last_trades['pnl'] < 0).sum()
    if recent_losses >= 4:
        score -= 15
        alerts.append("📉 Série de pertes récente")
    elif recent_losses >= 3:
        score -= 8
    
    # Clamp score
    score = max(0, min(100, score))
    
    # Déterminer le statut
    if score >= 80:
        status = 'excellent'
        emoji = '🟢'
    elif score >= 60:
        status = 'good'
        emoji = '🟡'
    elif score >= 40:
        status = 'warning'
        emoji = '🟠'
    else:
        status = 'tilt'
        emoji = '🔴'
    
    return {
        'score': score,
        'status': status,
        'emoji': emoji,
        'alerts': alerts,
        'revenge_pct': round(revenge_pct, 1),
        'avg_trades_per_day': round(avg_trades, 1),
        'impulsive_pct': round(impulsive_pct, 1)
    }
