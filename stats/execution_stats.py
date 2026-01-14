"""
stats/execution_stats.py - Statistiques d'exécution (Fees)
"""
import pandas as pd

def calculate_execution_stats(df: pd.DataFrame) -> dict:
    if len(df) == 0:
        return {}
    fees_total = df['fees'].abs().sum() if 'fees' in df.columns else 0
    pnl_net = df['pnl'].sum()
    pnl_brut = pnl_net + fees_total
    fees_pct = (fees_total / abs(pnl_brut)) * 100 if pnl_brut != 0 else 0
    return {
        'fees_total': round(fees_total, 2),
        'fees_mean': round(df['fees'].abs().mean(), 2) if 'fees' in df.columns else 0,
        'pnl_net': round(pnl_net, 2),
        'pnl_brut': round(pnl_brut, 2),
        'fees_pct_of_pnl': round(fees_pct, 1),
        'nb_trades': len(df)
    }

def format_execution_summary(stats: dict) -> str:
    return f"""
💼 EXÉCUTION & FEES
PnL Brut: {stats.get('pnl_brut', 0):.2f}$
Fees totales: {stats.get('fees_total', 0):.2f}$
PnL Net: {stats.get('pnl_net', 0):.2f}$
% PnL mangé par fees: {stats.get('fees_pct_of_pnl', 0):.1f}%
"""
