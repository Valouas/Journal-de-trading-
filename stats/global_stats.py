"""
stats/global_stats.py - Statistiques de performance globale

Calcule les métriques globales de performance:
- PnL Net/Brut, Profit Factor, Expectancy
- Sharpe, Drawdown, Recovery Factor
"""

import pandas as pd
import numpy as np


def calculate_global_stats(df: pd.DataFrame) -> dict:
    """
    Calcule toutes les statistiques de performance globale.
    
    Args:
        df: DataFrame des trades normalisés
    
    Returns:
        Dict avec toutes les métriques
    """
    if len(df) == 0:
        return {}
    
    # PnL
    pnl_net = df['pnl'].sum()
    fees_total = df['fees'].abs().sum()
    pnl_brut = pnl_net + fees_total
    
    # Gains et pertes séparés
    gains = df[df['pnl'] > 0]['pnl'].sum()
    losses = abs(df[df['pnl'] < 0]['pnl'].sum())
    
    # Profit Factor
    profit_factor = gains / losses if losses > 0 else float('inf')
    
    # Expectancy (EV par trade)
    expectancy = pnl_net / len(df)
    
    # Sharpe simplifié (mean / std)
    pnl_std = df['pnl'].std()
    sharpe = df['pnl'].mean() / pnl_std if pnl_std > 0 else 0
    
    # Drawdown
    cumulative_pnl = df['pnl'].cumsum()
    rolling_max = cumulative_pnl.cummax()
    drawdowns = cumulative_pnl - rolling_max
    
    max_drawdown = drawdowns.min()
    avg_drawdown = drawdowns[drawdowns < 0].mean() if len(drawdowns[drawdowns < 0]) > 0 else 0
    
    # Recovery Factor
    recovery_factor = abs(pnl_net / max_drawdown) if max_drawdown < 0 else float('inf')
    
    # Win rate
    nb_wins = (df['pnl'] > 0).sum()
    nb_losses = (df['pnl'] < 0).sum()
    winrate = (nb_wins / len(df)) * 100
    
    # R:R moyen (gain moyen / perte moyenne)
    avg_win = df[df['pnl'] > 0]['pnl'].mean() if nb_wins > 0 else 0
    avg_loss = abs(df[df['pnl'] < 0]['pnl'].mean()) if nb_losses > 0 else 0
    avg_rr = avg_win / avg_loss if avg_loss > 0 else float('inf')
    
    return {
        'pnl_net': round(pnl_net, 2),
        'pnl_brut': round(pnl_brut, 2),
        'fees_total': round(fees_total, 2),
        'profit_factor': round(profit_factor, 2),
        'expectancy': round(expectancy, 2),
        'sharpe': round(sharpe, 2),
        'max_drawdown': round(max_drawdown, 2),
        'avg_drawdown': round(avg_drawdown, 2),
        'recovery_factor': round(recovery_factor, 2),
        'winrate': round(winrate, 1),
        'nb_trades': len(df),
        'nb_wins': int(nb_wins),
        'nb_losses': int(nb_losses),
        'avg_win': round(avg_win, 2),
        'avg_loss': round(avg_loss, 2),
        'avg_rr': round(avg_rr, 2),
        'total_gains': round(gains, 2),
        'total_losses': round(losses, 2)
    }


def format_global_stats(stats: dict) -> str:
    """
    Formate les stats globales en texte lisible.
    """
    lines = [
        "═══════════════════════════════════════",
        "      📊 PERFORMANCE GLOBALE           ",
        "═══════════════════════════════════════",
        "",
        f"💰 PnL Net: {stats['pnl_net']}$",
        f"💵 PnL Brut: {stats['pnl_brut']}$ (avant {stats['fees_total']}$ de fees)",
        "",
        f"📈 Profit Factor: {stats['profit_factor']}",
        f"🎯 Expectancy: {stats['expectancy']}$ / trade",
        f"📉 Sharpe Ratio: {stats['sharpe']}",
        "",
        f"⬇️ Drawdown Max: {stats['max_drawdown']}$",
        f"⬇️ Drawdown Moyen: {stats['avg_drawdown']}$",
        f"🔄 Recovery Factor: {stats['recovery_factor']}",
        "",
        f"✅ Win Rate: {stats['winrate']}%",
        f"📊 R:R Moyen: {stats['avg_rr']}",
        f"🔢 Trades: {stats['nb_trades']} ({stats['nb_wins']}W / {stats['nb_losses']}L)",
        "═══════════════════════════════════════",
    ]
    return "\n".join(lines)
