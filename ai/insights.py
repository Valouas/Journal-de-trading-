"""
ai/insights.py - Génération d'insights comportementaux

Génère des punchlines franches et inconfortables
basées sur l'analyse des trades.
"""

import random


def generate_main_punchline(pct_destructive: float, pct_false_good: float, 
                            total_pnl: float, winrate: float) -> str:
    """
    Génère la punchline principale basée sur le taux de trades destructeurs.
    
    Ton: franc, analytique, inconfortable.
    Aucune référence au marché.
    
    Args:
        pct_destructive: % de trades destructeurs
        pct_false_good: % de faux bons trades
        total_pnl: PnL total
        winrate: taux de réussite global
    
    Returns:
        Punchline principale
    """
    
    # Catégorisation selon le niveau de destruction
    if pct_destructive > 40:
        punchlines = [
            f"🔴 {pct_destructive:.0f}% de tes trades sont auto-destructeurs. Tu ne trades pas, tu donnes ton argent.",
            f"🔴 Près de la moitié de tes trades ({pct_destructive:.0f}%) sont du sabotage. Tu es ton propre ennemi.",
            f"🔴 {pct_destructive:.0f}% de destruction. Ce n'est pas du trading, c'est de l'auto-mutilation financière.",
        ]
    elif pct_destructive > 25:
        punchlines = [
            f"🟠 {pct_destructive:.0f}% de trades destructeurs. Un quart de ton activité te coûte de l'argent.",
            f"🟠 1 trade sur 4 est destructeur ({pct_destructive:.0f}%). Ton ego te coûte cher.",
            f"🟠 {pct_destructive:.0f}% de tes décisions sont impulsives. Tu confonds action et performance.",
        ]
    elif pct_destructive > 10:
        punchlines = [
            f"🟡 {pct_destructive:.0f}% de trades destructeurs. Tu peux faire mieux.",
            f"🟡 Encore {pct_destructive:.0f}% de trades sabotés. Chaque % compte.",
            f"🟡 {pct_destructive:.0f}% de tes trades sont évitables. La discipline est un choix.",
        ]
    else:
        punchlines = [
            f"🟢 Seulement {pct_destructive:.0f}% de trades destructeurs. Discipline solide.",
            f"🟢 {pct_destructive:.0f}% de destruction. Tu fais partie des traders disciplinés.",
            f"🟢 Moins de 10% de trades destructeurs. Maintiens ce niveau.",
        ]
    
    main = random.choice(punchlines)
    
    # Ajouter un contexte sur les faux bons trades
    if pct_false_good > 20:
        main += f"\n⚠️ Attention: {pct_false_good:.0f}% de tes gains viennent de trades indisciplinés. Profits chanceux."
    
    return main


def generate_direction_insight(long_pnl: float, short_pnl: float, 
                               long_count: int, short_count: int) -> str:
    """
    Génère un insight sur la performance par direction.
    """
    total_trades = long_count + short_count
    if total_trades == 0:
        return ""
    
    long_pct = (long_count / total_trades) * 100
    short_pct = (short_count / total_trades) * 100
    
    if long_pnl > 0 and short_pnl < 0:
        return f"📈 Tu es rentable en LONG (+{long_pnl:.2f}$) mais tu perds en SHORT ({short_pnl:.2f}$). Arrête les shorts."
    elif short_pnl > 0 and long_pnl < 0:
        return f"📉 Tu es rentable en SHORT (+{short_pnl:.2f}$) mais tu perds en LONG ({long_pnl:.2f}$). Arrête les longs."
    elif long_pnl < 0 and short_pnl < 0:
        return f"💀 Tu perds dans les deux directions. LONG: {long_pnl:.2f}$ | SHORT: {short_pnl:.2f}$. Problème de gestion."
    else:
        better = "LONG" if long_pnl > short_pnl else "SHORT"
        return f"✅ Rentable des deux côtés. Edge plus fort en {better}."


def generate_temporal_insight(hourly_stats: dict) -> str:
    """
    Génère un insight sur les patterns temporels.
    
    Args:
        hourly_stats: Dict avec {hour: {'pnl': x, 'count': y, 'winrate': z}}
    """
    if not hourly_stats:
        return ""
    
    # Trouver les heures les plus profitables et les plus destructrices
    sorted_hours = sorted(hourly_stats.items(), key=lambda x: x[1].get('pnl', 0))
    
    worst_hours = [h for h, s in sorted_hours[:3] if s.get('pnl', 0) < 0]
    best_hours = [h for h, s in sorted_hours[-3:] if s.get('pnl', 0) > 0]
    
    insights = []
    
    if worst_hours:
        insights.append(f"🚫 Heures toxiques: {', '.join(f'{h}h' for h in worst_hours)}")
    
    if best_hours:
        insights.append(f"✅ Heures profitables: {', '.join(f'{h}h' for h in best_hours)}")
    
    return " | ".join(insights) if insights else ""


def generate_behavioral_insight(revenge_trades: int, impulse_trades: int, 
                                total_trades: int) -> str:
    """
    Génère un insight sur les patterns comportementaux.
    """
    if total_trades == 0:
        return ""
    
    revenge_pct = (revenge_trades / total_trades) * 100
    impulse_pct = (impulse_trades / total_trades) * 100
    
    insights = []
    
    if revenge_pct > 15:
        insights.append(f"🔥 {revenge_pct:.0f}% de revenge trading détecté")
    
    if impulse_pct > 20:
        insights.append(f"⚡ {impulse_pct:.0f}% de trades impulsifs (<5min après le précédent)")
    
    if not insights:
        return "✅ Pas de pattern de revenge trading ou d'impulsivité majeur détecté"
    
    return " | ".join(insights)


def generate_all_insights(df, stats: dict) -> dict:
    """
    Génère tous les insights à partir des données analysées.
    
    Args:
        df: DataFrame des trades analysés
        stats: Dict avec les statistiques calculées
    
    Returns:
        Dict avec tous les insights textuels
    """
    # Calculer les métriques nécessaires
    pct_destructive = (df['is_destructive'].sum() / len(df)) * 100 if len(df) > 0 else 0
    pct_false_good = (df['is_false_good'].sum() / len(df)) * 100 if len(df) > 0 else 0
    total_pnl = df['pnl'].sum()
    winrate = (df['is_win'].sum() / len(df)) * 100 if len(df) > 0 else 0
    
    # Stats par direction
    long_df = df[df['direction'] == 'LONG']
    short_df = df[df['direction'] == 'SHORT']
    long_pnl = long_df['pnl'].sum() if len(long_df) > 0 else 0
    short_pnl = short_df['pnl'].sum() if len(short_df) > 0 else 0
    
    # Revenge & impulse trades
    revenge_trades = (df['prev_loss_streak'] >= 5).sum() if 'prev_loss_streak' in df.columns else 0
    impulse_trades = (df['time_since_prev'] < 5).sum() if 'time_since_prev' in df.columns else 0
    
    return {
        'main_punchline': generate_main_punchline(pct_destructive, pct_false_good, total_pnl, winrate),
        'direction_insight': generate_direction_insight(long_pnl, short_pnl, len(long_df), len(short_df)),
        'behavioral_insight': generate_behavioral_insight(revenge_trades, impulse_trades, len(df)),
    }
