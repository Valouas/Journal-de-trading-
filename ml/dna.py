"""
ml/dna.py - Extraction du Trade DNA

Identifie le cluster avec le meilleur PnL total
et extrait le profil de trading optimal.
"""

import pandas as pd
import numpy as np


def extract_trade_dna(df: pd.DataFrame) -> dict:
    """
    Extrait le "Trade DNA" - le profil de trading le plus rentable.
    
    Le Trade DNA est basé sur le cluster avec le PnL total le plus élevé.
    
    Args:
        df: DataFrame avec les trades clusterisés
    
    Returns:
        Dict avec le profil DNA
    """
    if 'cluster' not in df.columns:
        raise ValueError("Les trades doivent être clusterisés d'abord")
    
    # Trouver le cluster avec le meilleur PnL
    cluster_pnl = df.groupby('cluster')['pnl'].sum()
    best_cluster = cluster_pnl.idxmax()
    
    # Filtrer les trades du meilleur cluster
    dna_trades = df[df['cluster'] == best_cluster]
    
    # Extraire le profil
    dna = {
        'cluster_id': int(best_cluster),
        'nb_trades': len(dna_trades),
        'pnl_total': dna_trades['pnl'].sum(),
        'pnl_moyen': dna_trades['pnl'].mean(),
        
        # Durée
        'duree_mediane_min': dna_trades['duration_minutes'].median(),
        'duree_moyenne_min': dna_trades['duration_minutes'].mean(),
        
        # Timing
        'heure_dominante': int(dna_trades['hour'].mode().iloc[0]) if len(dna_trades['hour'].mode()) > 0 else int(dna_trades['hour'].median()),
        'session_dominante': dna_trades['session'].mode().iloc[0] if len(dna_trades['session'].mode()) > 0 else 'Mixte',
        
        # Direction
        'direction_dominante': dna_trades['direction'].mode().iloc[0] if len(dna_trades['direction'].mode()) > 0 else 'MIXED',
        'pct_long': (dna_trades['direction'] == 'LONG').mean() * 100,
        'pct_short': (dna_trades['direction'] == 'SHORT').mean() * 100,
        
        # Discipline
        'discipline_moyenne': dna_trades['discipline_score'].mean(),
        'discipline_mediane': dna_trades['discipline_score'].median(),
        
        # Performance
        'winrate': (dna_trades['is_win'].sum() / len(dna_trades)) * 100,
        
        # Actifs favoris
        'top_symbols': dna_trades['symbol'].value_counts().head(3).to_dict()
    }
    
    return dna


def format_trade_dna(dna: dict) -> str:
    """
    Formate le Trade DNA en texte lisible.
    
    Args:
        dna: Dict du Trade DNA
    
    Returns:
        Chaîne formatée
    """
    lines = [
        "═══════════════════════════════════════",
        "           🧬 TRADE DNA               ",
        "═══════════════════════════════════════",
        "",
        f"📊 Performance",
        f"   PnL Total: {dna['pnl_total']:.2f}$",
        f"   Win Rate: {dna['winrate']:.1f}%",
        f"   Trades: {dna['nb_trades']}",
        "",
        f"⏱️ Timing optimal",
        f"   Durée médiane: {dna['duree_mediane_min']:.1f} min",
        f"   Heure: {dna['heure_dominante']}h",
        f"   Session: {dna['session_dominante']}",
        "",
        f"🎯 Direction",
        f"   Dominante: {dna['direction_dominante']}",
        f"   LONG: {dna['pct_long']:.1f}% | SHORT: {dna['pct_short']:.1f}%",
        "",
        f"📏 Discipline",
        f"   Score moyen: {dna['discipline_moyenne']:.1f}/100",
        "",
        "═══════════════════════════════════════",
    ]
    
    return "\n".join(lines)


def get_dna_recommendations(dna: dict, df: pd.DataFrame) -> list:
    """
    Génère des recommandations basées sur le Trade DNA.
    
    Returns:
        Liste de recommandations textuelles
    """
    recommendations = []
    
    # Recommandation sur la direction
    if dna['pct_long'] > 70:
        recommendations.append(f"🎯 Focus sur les positions LONG - c'est ton edge ({dna['pct_long']:.0f}% de ton DNA)")
    elif dna['pct_short'] > 70:
        recommendations.append(f"🎯 Focus sur les positions SHORT - c'est ton edge ({dna['pct_short']:.0f}% de ton DNA)")
    
    # Recommandation sur le timing
    recommendations.append(f"⏰ Privilégie les trades autour de {dna['heure_dominante']}h (session {dna['session_dominante']})")
    
    # Recommandation sur la durée
    if dna['duree_mediane_min'] > 30:
        recommendations.append(f"⏳ Tes meilleurs trades durent {dna['duree_mediane_min']:.0f}min+ - évite le scalping")
    else:
        recommendations.append(f"⚡ Tes meilleurs trades sont rapides ({dna['duree_mediane_min']:.0f}min) - scalping efficace")
    
    # Recommandation sur la discipline
    if dna['discipline_moyenne'] > 80:
        recommendations.append("✅ Ton DNA a une excellente discipline - maintiens ce niveau")
    elif dna['discipline_moyenne'] < 60:
        recommendations.append("⚠️ Même tes meilleurs trades manquent de discipline - à surveiller")
    
    # Top symbols
    if dna['top_symbols']:
        top_3 = list(dna['top_symbols'].keys())[:3]
        recommendations.append(f"🪙 Actifs les plus rentables: {', '.join(top_3)}")
    
    return recommendations
