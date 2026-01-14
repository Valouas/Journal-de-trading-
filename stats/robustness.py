"""
stats/robustness.py - Analyse de robustesse (Monte Carlo)
Module optionnel activé par bouton.
"""
import pandas as pd
import numpy as np

def monte_carlo_simulation(df: pd.DataFrame, n_simulations: int = 1000) -> dict:
    """Simule n_simulations séquences aléatoires de trades."""
    if len(df) == 0:
        return {}
    pnls = df['pnl'].values
    results = []
    for _ in range(n_simulations):
        shuffled = np.random.permutation(pnls)
        cumsum = np.cumsum(shuffled)
        final_pnl = cumsum[-1]
        max_dd = (cumsum - np.maximum.accumulate(cumsum)).min()
        results.append({'final_pnl': final_pnl, 'max_dd': max_dd})
    results_df = pd.DataFrame(results)
    return {
        'mean_pnl': round(results_df['final_pnl'].mean(), 2),
        'median_pnl': round(results_df['final_pnl'].median(), 2),
        'pnl_5th': round(results_df['final_pnl'].quantile(0.05), 2),
        'pnl_95th': round(results_df['final_pnl'].quantile(0.95), 2),
        'worst_pnl': round(results_df['final_pnl'].min(), 2),
        'best_pnl': round(results_df['final_pnl'].max(), 2),
        'mean_dd': round(results_df['max_dd'].mean(), 2),
        'worst_dd': round(results_df['max_dd'].min(), 2),
    }

def calculate_rolling_expectancy(df: pd.DataFrame, window: int = 20) -> pd.Series:
    """Calcule l'expectancy sur fenêtre glissante."""
    if len(df) < window:
        return pd.Series()
    return df['pnl'].rolling(window=window).mean()

def format_robustness_summary(mc_stats: dict) -> str:
    return f"""
🧪 ANALYSE MONTE CARLO (1000 simulations)

PnL moyen: {mc_stats.get('mean_pnl', 0):.2f}$
PnL médian: {mc_stats.get('median_pnl', 0):.2f}$
Intervalle 90%: [{mc_stats.get('pnl_5th', 0):.2f}$, {mc_stats.get('pnl_95th', 0):.2f}$]
Pire scénario: {mc_stats.get('worst_pnl', 0):.2f}$
Meilleur scénario: {mc_stats.get('best_pnl', 0):.2f}$
Drawdown moyen: {mc_stats.get('mean_dd', 0):.2f}$
Pire drawdown: {mc_stats.get('worst_dd', 0):.2f}$
"""
