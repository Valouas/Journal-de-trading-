"""
stats/duration_stats.py - Statistiques de durée

Analyse du temps en position:
- Durée moyenne/médiane
- Performance par tranche de durée
- Comparaison wins vs losses
"""

import pandas as pd
import numpy as np


def calculate_duration_stats(df: pd.DataFrame) -> dict:
    """
    Calcule les statistiques de durée.
    
    Returns:
        Dict avec métriques de durée
    """
    if len(df) == 0 or 'duration_minutes' not in df.columns:
        return {}
    
    wins = df[df['is_win']]
    losses = df[~df['is_win']]
    
    return {
        'duration_mean': round(df['duration_minutes'].mean(), 1),
        'duration_median': round(df['duration_minutes'].median(), 1),
        'duration_min': round(df['duration_minutes'].min(), 1),
        'duration_max': round(df['duration_minutes'].max(), 1),
        'duration_std': round(df['duration_minutes'].std(), 1),
        
        # Comparaison wins vs losses
        'win_duration_mean': round(wins['duration_minutes'].mean(), 1) if len(wins) > 0 else 0,
        'win_duration_median': round(wins['duration_minutes'].median(), 1) if len(wins) > 0 else 0,
        'loss_duration_mean': round(losses['duration_minutes'].mean(), 1) if len(losses) > 0 else 0,
        'loss_duration_median': round(losses['duration_minutes'].median(), 1) if len(losses) > 0 else 0,
    }


def calculate_duration_brackets(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule les performances par tranche de durée.
    
    Tranches: 0-5min, 5-15min, 15-60min, 60min+
    """
    if len(df) == 0 or 'duration_minutes' not in df.columns:
        return pd.DataFrame()
    
    def get_bracket(duration):
        if duration < 5:
            return '0-5 min'
        elif duration < 15:
            return '5-15 min'
        elif duration < 60:
            return '15-60 min'
        else:
            return '60+ min'
    
    df = df.copy()
    df['duration_bracket'] = df['duration_minutes'].apply(get_bracket)
    
    brackets = df.groupby('duration_bracket').agg({
        'pnl': ['sum', 'mean', 'count'],
        'is_win': lambda x: (x.sum() / len(x)) * 100 if len(x) > 0 else 0,
        'discipline_score': 'mean'
    }).round(2)
    
    brackets.columns = ['pnl_total', 'pnl_moyen', 'nb_trades', 'winrate', 'discipline_moy']
    
    # Ordonner les tranches
    order = ['0-5 min', '5-15 min', '15-60 min', '60+ min']
    brackets = brackets.reset_index()
    brackets['order'] = brackets['duration_bracket'].apply(lambda x: order.index(x) if x in order else 99)
    brackets = brackets.sort_values('order').drop('order', axis=1)
    
    return brackets


def analyze_duration_impact(df: pd.DataFrame, stats: dict) -> str:
    """
    Analyse l'impact de la durée sur la performance.
    
    Returns:
        Insight textuel
    """
    insights = []
    
    # Comparaison durée wins vs losses
    win_dur = stats.get('win_duration_median', 0)
    loss_dur = stats.get('loss_duration_median', 0)
    
    if win_dur > 0 and loss_dur > 0:
        if win_dur > loss_dur * 1.5:
            insights.append(f"✅ Tes wins durent {win_dur:.0f}min vs {loss_dur:.0f}min pour les pertes. Laisse courir tes gagnants!")
        elif loss_dur > win_dur * 1.5:
            insights.append(f"⚠️ Tes pertes durent {loss_dur:.0f}min vs {win_dur:.0f}min pour les gains. Tu coupes tes gains trop tôt!")
    
    # Analyser les tranches
    brackets = calculate_duration_brackets(df)
    if len(brackets) > 0:
        best = brackets.loc[brackets['pnl_total'].idxmax()]
        worst = brackets.loc[brackets['pnl_total'].idxmin()]
        
        if best['pnl_total'] > 0:
            insights.append(f"🎯 Meilleure durée: {best['duration_bracket']} (+{best['pnl_total']:.2f}$)")
        if worst['pnl_total'] < 0:
            insights.append(f"🚫 Pire durée: {worst['duration_bracket']} ({worst['pnl_total']:.2f}$)")
    
    return "\n".join(insights) if insights else "Analyse de durée neutre"


def format_duration_summary(stats: dict, brackets: pd.DataFrame) -> str:
    """
    Formate le résumé des stats de durée.
    """
    lines = [
        "═══════════════════════════════════════",
        "         ⏱️ TEMPS EN POSITION          ",
        "═══════════════════════════════════════",
        "",
        f"📊 Durée moyenne: {stats.get('duration_mean', 0):.1f} min",
        f"📊 Durée médiane: {stats.get('duration_median', 0):.1f} min",
        "",
        "🏆 Trades gagnants:",
        f"   Durée moyenne: {stats.get('win_duration_mean', 0):.1f} min",
        f"   Durée médiane: {stats.get('win_duration_median', 0):.1f} min",
        "",
        "💀 Trades perdants:",
        f"   Durée moyenne: {stats.get('loss_duration_mean', 0):.1f} min",
        f"   Durée médiane: {stats.get('loss_duration_median', 0):.1f} min",
        ""
    ]
    
    if len(brackets) > 0:
        lines.append("📉 Performance par durée:")
        for _, row in brackets.iterrows():
            emoji = "🟢" if row['pnl_total'] > 0 else "🔴"
            lines.append(
                f"   {emoji} {row['duration_bracket']}: {row['pnl_total']:.2f}$ "
                f"(WR: {row['winrate']:.0f}%, {row['nb_trades']} trades)"
            )
    
    return "\n".join(lines)
