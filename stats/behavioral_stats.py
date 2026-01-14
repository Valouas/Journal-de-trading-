"""
stats/behavioral_stats.py - Statistiques comportementales

Détecte les patterns de:
- Revenge trading
- Overtrading
- Séquences de gains/pertes
- Impulsivité
"""

import pandas as pd
import numpy as np


def calculate_behavioral_stats(df: pd.DataFrame) -> dict:
    """
    Calcule les statistiques comportementales.
    
    Returns:
        Dict avec métriques comportementales
    """
    if len(df) == 0:
        return {}
    
    # Séquences de gains/pertes
    max_win_streak, max_loss_streak = calculate_max_streaks(df)
    
    # Trades après pertes consécutives
    pnl_after_losses = calculate_pnl_after_losses(df)
    
    # Trades rapides (revenge trading potentiel)
    quick_trades = df[df.get('time_since_prev', pd.Series([999]*len(df))) < 5]
    quick_trades_pnl = quick_trades['pnl'].sum() if len(quick_trades) > 0 else 0
    
    # Trades "patients" vs "rapides"
    if 'duration_minutes' in df.columns:
        median_duration = df['duration_minutes'].median()
        patient_trades = df[df['duration_minutes'] >= median_duration]
        quick_duration_trades = df[df['duration_minutes'] < median_duration]
        
        patient_pnl = patient_trades['pnl'].sum() if len(patient_trades) > 0 else 0
        quick_duration_pnl = quick_duration_trades['pnl'].sum() if len(quick_duration_trades) > 0 else 0
    else:
        patient_pnl = quick_duration_pnl = 0
    
    # Revenge trades (après 3+ pertes)
    # Revenge trading = trade après 5+ pertes consécutives
    revenge_trades = df[df.get('prev_loss_streak', pd.Series([0]*len(df))) >= 5]
    revenge_count = len(revenge_trades)
    revenge_pnl = revenge_trades['pnl'].sum() if revenge_count > 0 else 0
    
    return {
        'max_win_streak': max_win_streak,
        'max_loss_streak': max_loss_streak,
        'pnl_after_1_loss': pnl_after_losses.get(1, 0),
        'pnl_after_2_losses': pnl_after_losses.get(2, 0),
        'pnl_after_3_losses': pnl_after_losses.get(3, 0),
        'quick_entry_count': len(quick_trades),
        'quick_entry_pnl': round(quick_trades_pnl, 2),
        'quick_entry_pct': round((len(quick_trades) / len(df)) * 100, 1) if len(df) > 0 else 0,
        'patient_pnl': round(patient_pnl, 2),
        'quick_duration_pnl': round(quick_duration_pnl, 2),
        'revenge_count': revenge_count,
        'revenge_pnl': round(revenge_pnl, 2),
        'revenge_pct': round((revenge_count / len(df)) * 100, 1) if len(df) > 0 else 0
    }


def calculate_max_streaks(df: pd.DataFrame) -> tuple:
    """
    Calcule les séquences maximales de gains et pertes.
    
    Returns:
        (max_win_streak, max_loss_streak)
    """
    if len(df) == 0:
        return 0, 0
    
    max_win = max_loss = 0
    current_win = current_loss = 0
    
    for pnl in df['pnl']:
        if pnl > 0:
            current_win += 1
            current_loss = 0
            max_win = max(max_win, current_win)
        elif pnl < 0:
            current_loss += 1
            current_win = 0
            max_loss = max(max_loss, current_loss)
        else:
            current_win = current_loss = 0
    
    return max_win, max_loss


def calculate_pnl_after_losses(df: pd.DataFrame) -> dict:
    """
    Calcule le PnL des trades pris après 1, 2, 3+ pertes consécutives.
    
    Returns:
        Dict avec {nb_pertes: pnl_total}
    """
    if len(df) == 0 or 'prev_loss_streak' not in df.columns:
        return {}
    
    result = {}
    for n in [1, 2, 3]:
        trades_after_n = df[df['prev_loss_streak'] == n]
        result[n] = round(trades_after_n['pnl'].sum(), 2) if len(trades_after_n) > 0 else 0
    
    return result


def detect_behavioral_patterns(stats: dict) -> list:
    """
    Détecte les patterns comportementaux problématiques.
    
    Returns:
        Liste d'alertes textuelles
    """
    alerts = []
    
    # Revenge trading
    if stats.get('revenge_pct', 0) > 15:
        alerts.append({
            'type': 'REVENGE TRADING',
            'severity': 'HIGH',
            'message': f"🔥 {stats['revenge_pct']:.0f}% de tes trades sont du revenge trading (après 3+ pertes)",
            'impact': f"PnL de ces trades: {stats['revenge_pnl']:.2f}$"
        })
    
    # Overtrading (trades trop rapprochés)
    if stats.get('quick_entry_pct', 0) > 20:
        alerts.append({
            'type': 'OVERTRADING',
            'severity': 'HIGH',
            'message': f"⚡ {stats['quick_entry_pct']:.0f}% de tes trades sont pris <5min après le précédent",
            'impact': f"PnL de ces trades: {stats['quick_entry_pnl']:.2f}$"
        })
    
    # Impact de la patience
    if stats.get('patient_pnl', 0) > 0 and stats.get('quick_duration_pnl', 0) < 0:
        alerts.append({
            'type': 'IMPATIENCE',
            'severity': 'MEDIUM',
            'message': "⏳ Les trades patients sont rentables, les trades courts perdent",
            'impact': f"Patient: +{stats['patient_pnl']:.2f}$ | Rapide: {stats['quick_duration_pnl']:.2f}$"
        })
    
    # Séquence de pertes longue
    if stats.get('max_loss_streak', 0) >= 5:
        alerts.append({
            'type': 'TILT POTENTIEL',
            'severity': 'MEDIUM',
            'message': f"📉 Séquence de {stats['max_loss_streak']} pertes consécutives détectée",
            'impact': "Risque de tilt et de décisions émotionnelles"
        })
    
    # PnL après pertes
    if stats.get('pnl_after_3_losses', 0) < 0:
        alerts.append({
            'type': 'POST-LOSS BEHAVIOR',
            'severity': 'HIGH',
            'message': f"💀 Tes trades après 3 pertes perdent encore {abs(stats['pnl_after_3_losses']):.2f}$",
            'impact': "Tu devrais arrêter de trader après 3 pertes"
        })
    
    return alerts


def format_behavioral_summary(stats: dict) -> str:
    """
    Formate le résumé des stats comportementales.
    """
    lines = [
        "═══════════════════════════════════════",
        "       🧠 PATTERNS COMPORTEMENTAUX     ",
        "═══════════════════════════════════════",
        "",
        f"🏆 Série de gains max: {stats.get('max_win_streak', 0)}",
        f"💀 Série de pertes max: {stats.get('max_loss_streak', 0)}",
        "",
        f"🔥 Revenge trades: {stats.get('revenge_count', 0)} ({stats.get('revenge_pct', 0):.0f}%)",
        f"   PnL revenge: {stats.get('revenge_pnl', 0):.2f}$",
        "",
        f"⚡ Trades <5min après précédent: {stats.get('quick_entry_count', 0)} ({stats.get('quick_entry_pct', 0):.0f}%)",
        f"   PnL: {stats.get('quick_entry_pnl', 0):.2f}$",
        "",
        "📊 PnL après pertes consécutives:",
        f"   Après 1 perte: {stats.get('pnl_after_1_loss', 0):.2f}$",
        f"   Après 2 pertes: {stats.get('pnl_after_2_losses', 0):.2f}$",
        f"   Après 3 pertes: {stats.get('pnl_after_3_losses', 0):.2f}$",
        "",
        f"⏳ Trades patients: {stats.get('patient_pnl', 0):.2f}$",
        f"⚡ Trades rapides: {stats.get('quick_duration_pnl', 0):.2f}$",
        "═══════════════════════════════════════",
    ]
    return "\n".join(lines)
