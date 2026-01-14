"""
stats/risk_stats.py - Statistiques de gestion du risque

Analyse par levier, taille de position.
"""

import pandas as pd
import numpy as np


def calculate_risk_stats(df: pd.DataFrame) -> dict:
    """
    Calcule les statistiques de risque.
    
    Returns:
        Dict avec métriques de risque
    """
    if len(df) == 0 or 'leverage' not in df.columns:
        return {}
    
    return {
        'leverage_mean': round(df['leverage'].mean(), 1),
        'leverage_median': round(df['leverage'].median(), 1),
        'leverage_max': round(df['leverage'].max(), 1),
        'leverage_min': round(df['leverage'].min(), 1),
    }


def calculate_leverage_brackets(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule les performances par tranche de levier.
    
    Tranches: <20x, 20-40x, 40x+
    """
    if len(df) == 0 or 'leverage' not in df.columns:
        return pd.DataFrame()
    
    # Créer les tranches
    def get_bracket(lev):
        if lev < 20:
            return '<20x'
        elif lev < 40:
            return '20-40x'
        else:
            return '40x+'
    
    df = df.copy()
    df['leverage_bracket'] = df['leverage'].apply(get_bracket)
    
    # Statistiques par tranche
    brackets = df.groupby('leverage_bracket').agg({
        'pnl': ['sum', 'mean', 'count'],
        'is_win': lambda x: (x.sum() / len(x)) * 100 if len(x) > 0 else 0,
        'discipline_score': 'mean'
    }).round(2)
    
    brackets.columns = ['pnl_total', 'pnl_moyen', 'nb_trades', 'winrate', 'discipline_moy']
    
    # Ordonner les tranches
    order = ['<20x', '20-40x', '40x+']
    brackets = brackets.reset_index()
    brackets['order'] = brackets['leverage_bracket'].apply(lambda x: order.index(x) if x in order else 99)
    brackets = brackets.sort_values('order').drop('order', axis=1)
    
    return brackets


def analyze_leverage_impact(df: pd.DataFrame) -> str:
    """
    Analyse l'impact du levier sur la performance.
    
    Returns:
        Insight textuel sur le levier
    """
    brackets = calculate_leverage_brackets(df)
    
    if len(brackets) == 0:
        return "Données de levier non disponibles"
    
    # Trouver la meilleure et pire tranche
    best = brackets.loc[brackets['pnl_total'].idxmax()]
    worst = brackets.loc[brackets['pnl_total'].idxmin()]
    
    insights = []
    
    # Comparer les tranches
    high_lev = brackets[brackets['leverage_bracket'] == '40x+']
    low_lev = brackets[brackets['leverage_bracket'] == '<20x']
    
    if len(high_lev) > 0 and len(low_lev) > 0:
        high_pnl = high_lev.iloc[0]['pnl_total']
        low_pnl = low_lev.iloc[0]['pnl_total']
        
        if high_pnl < 0 and low_pnl > 0:
            insights.append(f"⚠️ Le levier élevé (40x+) te coûte {abs(high_pnl):.2f}$ alors que le levier faible est rentable")
        elif high_pnl > low_pnl and high_pnl > 0:
            insights.append(f"📈 Le levier élevé est plus rentable (+{high_pnl:.2f}$) mais attention au risque")
    
    if best['pnl_total'] > 0:
        insights.append(f"✅ Meilleure tranche: {best['leverage_bracket']} (PnL: +{best['pnl_total']:.2f}$)")
    
    if worst['pnl_total'] < 0:
        insights.append(f"🚫 Pire tranche: {worst['leverage_bracket']} (PnL: {worst['pnl_total']:.2f}$)")
    
    return "\n".join(insights) if insights else "Analyse du levier neutre"


def format_risk_summary(stats: dict, brackets: pd.DataFrame) -> str:
    """
    Formate le résumé des stats de risque.
    """
    lines = [
        "═══════════════════════════════════════",
        "        ⚖️ GESTION DU RISQUE           ",
        "═══════════════════════════════════════",
        "",
        f"📊 Levier moyen: {stats.get('leverage_mean', 'N/A')}x",
        f"📊 Levier médian: {stats.get('leverage_median', 'N/A')}x",
        f"📈 Levier max: {stats.get('leverage_max', 'N/A')}x",
        ""
    ]
    
    if len(brackets) > 0:
        lines.append("📉 Performance par tranche de levier:")
        for _, row in brackets.iterrows():
            emoji = "🟢" if row['pnl_total'] > 0 else "🔴"
            lines.append(
                f"   {emoji} {row['leverage_bracket']}: {row['pnl_total']:.2f}$ "
                f"(WR: {row['winrate']:.0f}%, {row['nb_trades']} trades)"
            )
    
    return "\n".join(lines)
