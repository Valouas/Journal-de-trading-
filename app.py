"""
# Trade Behavior Audit
# Copyright (C) 2026 <ton_pseudo>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
Trade Behavior Audit - Application Streamlit
Analyse comportementale des trades MEXC Futures

Usage: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_loader import normalize_data
from ml.scoring import calculate_discipline_score, label_trades, get_discipline_summary
from ml.clustering import perform_clustering, get_cluster_profiles, get_cluster_summary
from ml.dna import extract_trade_dna, get_dna_recommendations
from ai.insights import generate_all_insights
from stats.global_stats import calculate_global_stats
from stats.direction_stats import calculate_direction_stats, format_direction_comparison
from stats.temporal_stats import (calculate_hourly_stats, calculate_session_stats, 
                                   calculate_daily_stats, get_toxic_hours, get_profitable_hours)
from stats.asset_stats import calculate_asset_stats, calculate_cross_analysis
from stats.risk_stats import calculate_risk_stats, calculate_leverage_brackets, analyze_leverage_impact
from stats.behavioral_stats import calculate_behavioral_stats, detect_behavioral_patterns
from stats.duration_stats import calculate_duration_stats, calculate_duration_brackets
from stats.execution_stats import calculate_execution_stats
from stats.robustness import monte_carlo_simulation, format_robustness_summary
from stats.visualizations import generate_equity_curve_data, generate_calendar_heatmap_data, get_pnl_color
from stats.trade_types import add_trade_type_column, calculate_trade_type_stats, calculate_trade_type_by_direction, calculate_tiltmeter

# ----- CONFIG -----
st.set_page_config(
    page_title="Trade Behavior Audit",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----- SIDEBAR -----
st.sidebar.title("🧠 Trade Audit")

# Navigation section
st.sidebar.markdown("### 🧭 Navigation")
nav_sections = {
    "🔝 Haut de page": "top",
    "📊 Résumé Brutal": "resume",
    "📈 Equity Curve": "equity", 
    "📅 Calendrier": "calendar",
    "🎯 Performance": "performance",
    "🔀 Long vs Short": "direction",
    "⏰ Temporel": "temporal",
    "🪙 Actifs": "assets",
    "⚖️ Risque/Levier": "risk",
    "🎲 Trade Types": "tradetypes",
    "🧬 Trade DNA": "dna",
    "🎯 Clusters": "clusters",
    "🧠 Comportement": "behavior",
    "⏱️ Durée": "duration",
    "💀 Problèmes": "problems",
    "🔬 Monte Carlo": "montecarlo"
}
selected_nav = st.sidebar.selectbox("Aller à la section", list(nav_sections.keys()), label_visibility="collapsed")

# Quick stats placeholder
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Quick Stats")
quick_stats_placeholder = st.sidebar.empty()

# Tiltmeter section
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎚️ Tiltmeter")
tiltmeter_placeholder = st.sidebar.empty()

# Asset filter section
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 Filtres")
asset_filter_placeholder = st.sidebar.empty()

# ----- STYLES -----
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #6c5ce7;
    }
    .destructive { border-left-color: #e74c3c; }
    .positive { border-left-color: #2ecc71; }
    .warning { border-left-color: #f39c12; }
    .stMetric {
        background: rgba(255,255,255,0.05);
        padding: 1rem;
        border-radius: 8px;
    }
    .tiltmeter-good { color: #2ecc71; font-size: 2em; }
    .tiltmeter-warning { color: #f39c12; font-size: 2em; }
    .tiltmeter-danger { color: #e74c3c; font-size: 2em; }
</style>
""", unsafe_allow_html=True)

# ----- SCROLL NAVIGATION -----
# Add top anchor
st.markdown('<div id="top"></div>', unsafe_allow_html=True)

# Scroll to selected section using JavaScript
if selected_nav and selected_nav != "🔝 Haut de page":
    anchor_id = nav_sections[selected_nav]
    st.markdown(f"""
    <script>
        var element = document.getElementById('{anchor_id}');
        if (element) {{
            element.scrollIntoView({{behavior: 'smooth', block: 'start'}});
        }}
    </script>
    """, unsafe_allow_html=True)

# ----- HEADER -----
st.title("🧠 Trade Behavior Audit")
st.markdown("*Analyse comportementale de tes trades MEXC Futures*")
st.markdown("---")

# ----- AUTO-DETECT FILES IN APP FOLDER -----
APP_DIR = os.path.dirname(os.path.abspath(__file__))

def find_mexc_files():
    """
    Cherche automatiquement les fichiers MEXC dans le dossier de l'app.
    Returns: (positions_path, orders_path) ou (None, None)
    """
    positions_file = None
    orders_file = None
    
    for filename in os.listdir(APP_DIR):
        filepath = os.path.join(APP_DIR, filename)
        if not os.path.isfile(filepath):
            continue
        if not filename.endswith(('.xlsx', '.xls', '.csv')):
            continue
        
        filename_lower = filename.lower()
        
        # Détecter fichier positions
        if 'position' in filename_lower and 'history' in filename_lower:
            positions_file = filepath
        elif 'position' in filename_lower and 'mexc' in filename_lower:
            positions_file = filepath
            
        # Détecter fichier ordres
        if 'ordre' in filename_lower or 'order' in filename_lower:
            orders_file = filepath
        elif 'historique' in filename_lower and 'contrat' in filename_lower:
            orders_file = filepath
    
    return positions_file, orders_file

# Chercher les fichiers automatiquement
auto_positions, auto_orders = find_mexc_files()

# ----- SOURCE DE DONNÉES -----
if auto_positions and auto_orders:
    # Mode automatique - fichiers trouvés dans le dossier
    st.success(f"📂 Fichiers MEXC détectés automatiquement dans le dossier")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"📊 Positions: `{os.path.basename(auto_positions)}`")
    with col2:
        st.info(f"📋 Ordres: `{os.path.basename(auto_orders)}`")
    
    positions_file = auto_positions
    orders_file = auto_orders
    use_file_path = True
else:
    # Mode upload manuel
    st.header("📂 1. Upload des fichiers MEXC")
    st.caption("💡 Astuce: Place tes fichiers MEXC dans le même dossier que app.py pour un chargement automatique")
    
    col1, col2 = st.columns(2)
    
    with col1:
        positions_file = st.file_uploader(
            "📊 Historique des POSITIONS", 
            type=['csv', 'xlsx'],
            help="Fichier MEXC 'Position History'"
        )
    
    with col2:
        orders_file = st.file_uploader(
            "📋 Historique des ORDRES", 
            type=['csv', 'xlsx'],
            help="Fichier MEXC 'Historique des ordres'"
        )
    
    use_file_path = False
    
    # Check if both files are uploaded
    if positions_file is None or orders_file is None:
        st.warning("⚠️ Upload les 2 fichiers MEXC pour commencer l'analyse")
        st.stop()

st.markdown("---")

# ----- PROCESS DATA -----
with st.spinner("🔄 Chargement et normalisation des données..."):
    try:
        if use_file_path:
            # Charger depuis les chemins de fichiers
            import pandas as pd
            if positions_file.endswith('.csv'):
                df_pos = pd.read_csv(positions_file)
            else:
                df_pos = pd.read_excel(positions_file)
            
            if orders_file.endswith('.csv'):
                df_ord = pd.read_csv(orders_file)
            else:
                df_ord = pd.read_excel(orders_file)
            
            from data_loader import normalize_positions, enrich_with_orders
            df = normalize_positions(df_pos)
            df = enrich_with_orders(df, df_ord)
            df = df.sort_values('close_time').reset_index(drop=True)
        else:
            # Charger depuis les fichiers uploadés
            df = normalize_data(positions_file, orders_file)
        
        df = calculate_discipline_score(df)
        df = label_trades(df)
        df = perform_clustering(df)
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        st.stop()

st.success(f"✅ {len(df)} trades chargés et analysés")
st.markdown("---")

# ----- CALCULATE ALL STATS -----
global_stats = calculate_global_stats(df)
direction_stats = calculate_direction_stats(df)
discipline_summary = get_discipline_summary(df)
insights = generate_all_insights(df, global_stats)
hourly_stats = calculate_hourly_stats(df)
session_stats = calculate_session_stats(df)
daily_stats = calculate_daily_stats(df)
asset_stats = calculate_asset_stats(df)
risk_stats = calculate_risk_stats(df)
leverage_brackets = calculate_leverage_brackets(df)
behavioral_stats = calculate_behavioral_stats(df)
duration_stats = calculate_duration_stats(df)
duration_brackets = calculate_duration_brackets(df)
execution_stats = calculate_execution_stats(df)
cluster_profiles = get_cluster_profiles(df)

# Add trade type classification
df = add_trade_type_column(df)
trade_type_stats = calculate_trade_type_stats(df)
trade_type_by_direction = calculate_trade_type_by_direction(df)

# Calculate Tiltmeter
tiltmeter = calculate_tiltmeter(df)

# Update Quick Stats in sidebar
with quick_stats_placeholder:
    st.metric("Trades", len(df))
    st.metric("PnL", f"{df['pnl'].sum():.0f}$")
    st.metric("Win Rate", f"{(df['pnl'] > 0).mean()*100:.0f}%")

# Update Tiltmeter in sidebar
tiltmeter_placeholder.markdown(f"**{tiltmeter['emoji']} {tiltmeter['score']}/100**")
if tiltmeter['status'] == 'tilt':
    st.sidebar.error("⚠️ EN TILT!")
for alert in tiltmeter['alerts'][:2]:
    st.sidebar.caption(alert)

# Asset filter in sidebar
all_symbols = sorted(df['symbol'].unique().tolist())
with asset_filter_placeholder:
    selected_symbols = st.multiselect(
        "Filtrer par actif",
        options=all_symbols,
        default=None,
        placeholder="Tous les actifs",
        key="asset_filter"
    )

# Apply asset filter - if empty means all, if has selection means filter
if selected_symbols and len(selected_symbols) > 0:
    df_filtered = df[df['symbol'].isin(selected_symbols)].copy()
    st.info(f"🔍 Filtre actif: {', '.join(selected_symbols)} ({len(df_filtered)} trades)")
    
    # Recalculate ALL stats with filtered data
    global_stats = calculate_global_stats(df_filtered)
    direction_stats = calculate_direction_stats(df_filtered)
    discipline_summary = get_discipline_summary(df_filtered)
    insights = generate_all_insights(df_filtered, global_stats)
    hourly_stats = calculate_hourly_stats(df_filtered)
    session_stats = calculate_session_stats(df_filtered)
    daily_stats = calculate_daily_stats(df_filtered)
    asset_stats = calculate_asset_stats(df_filtered)
    trade_type_stats = calculate_trade_type_stats(df_filtered)
    trade_type_by_direction = calculate_trade_type_by_direction(df_filtered)
    
    # Also recalculate bottom section stats
    risk_stats = calculate_risk_stats(df_filtered)
    leverage_brackets = calculate_leverage_brackets(df_filtered)
    behavioral_stats = calculate_behavioral_stats(df_filtered)
    duration_stats = calculate_duration_stats(df_filtered)
    duration_brackets = calculate_duration_brackets(df_filtered)
    execution_stats = calculate_execution_stats(df_filtered)
    cluster_profiles = get_cluster_profiles(df_filtered)
else:
    df_filtered = df

try:
    trade_dna = extract_trade_dna(df_filtered)
    dna_recommendations = get_dna_recommendations(trade_dna, df_filtered)
except:
    trade_dna = None
    dna_recommendations = []

# ===== SECTION 1: RÉSUMÉ BRUTAL =====
st.markdown('<div id="resume"></div>', unsafe_allow_html=True)
st.header("🔥 Résumé Brutal")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📏 Discipline Moyenne", f"{discipline_summary['avg_score']:.0f}/100")
with col2:
    color = "normal" if global_stats['pnl_net'] >= 0 else "inverse"
    st.metric("💰 PnL Net", f"{global_stats['pnl_net']:.2f}$")
with col3:
    st.metric("📊 Trades", global_stats['nb_trades'])
with col4:
    st.metric("💀 Trades Destructeurs", f"{discipline_summary['pct_destructive']:.1f}%")

# AI Punchline
st.markdown("### 🎯 Verdict IA")
st.info(insights['main_punchline'])
if insights['direction_insight']:
    st.warning(insights['direction_insight'])
st.markdown("---")

# ===== SECTION: EQUITY CURVE =====
st.markdown('<div id="equity"></div>', unsafe_allow_html=True)
st.header("📈 Equity Curve")

# Generate equity curve data
equity_data = generate_equity_curve_data(df)
if len(equity_data) > 0:
    # Create static chart with matplotlib (no zoom interaction)
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    
    fig, ax = plt.subplots(figsize=(12, 4))
    fig.patch.set_facecolor('#0e1117')
    ax.set_facecolor('#0e1117')
    
    # Plot cumulative PnL
    ax.plot(equity_data['close_time'], equity_data['cumulative_pnl'], 
            color='#00d4aa', linewidth=2, label='PnL Cumulé')
    
    # Fill area under curve
    ax.fill_between(equity_data['close_time'], equity_data['cumulative_pnl'], 
                    alpha=0.3, color='#00d4aa')
    
    # Add zero line
    ax.axhline(y=0, color='#666', linestyle='--', linewidth=0.5)
    
    # Styling
    ax.set_ylabel('PnL ($)', color='white')
    ax.tick_params(colors='white')
    ax.spines['bottom'].set_color('#333')
    ax.spines['left'].set_color('#333')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
    ax.grid(True, alpha=0.2, color='#444')
    
    plt.tight_layout()
    st.pyplot(fig, width='stretch')
    plt.close(fig)
    
    # Show key stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        peak = equity_data['cumulative_pnl'].max()
        st.metric("🔝 Peak", f"{peak:.2f}$")
    with col2:
        final = equity_data['cumulative_pnl'].iloc[-1]
        st.metric("🏁 Final", f"{final:.2f}$")
    with col3:
        dd = (equity_data['cumulative_pnl'] - equity_data['cumulative_pnl'].cummax()).min()
        st.metric("📉 Max Drawdown", f"{dd:.2f}$")
    with col4:
        best_trade = equity_data['pnl'].max()
        st.metric("🎯 Meilleur Trade", f"+{best_trade:.2f}$")

st.markdown("---")

# ===== SECTION: CALENDAR HEATMAP =====
st.markdown('<div id="calendar"></div>', unsafe_allow_html=True)
st.header("📅 Calendar Heatmap")

calendar_data = generate_calendar_heatmap_data(df)
if len(calendar_data) > 0:
    # Get available months
    months_available = calendar_data.groupby(['year', 'month']).size().reset_index()
    month_names = ['Jan','Fév','Mar','Avr','Mai','Juin','Juil','Août','Sep','Oct','Nov','Déc']
    months_available['label'] = months_available.apply(
        lambda r: f"{month_names[int(r['month'])-1]} {int(r['year'])}", 
        axis=1
    )
    
    # Month selector
    if len(months_available) > 1:
        selected_month_label = st.selectbox("Sélectionner le mois", months_available['label'].tolist())
        selected_idx = months_available[months_available['label'] == selected_month_label].index[0]
        selected_year = int(months_available.loc[selected_idx, 'year'])
        selected_month = int(months_available.loc[selected_idx, 'month'])
    else:
        selected_year = int(months_available.iloc[0]['year'])
        selected_month = int(months_available.iloc[0]['month'])
    
    # Filter data for selected month
    month_data = calendar_data[
        (calendar_data['year'] == selected_year) & 
        (calendar_data['month'] == selected_month)
    ]
    
    # Calculate max PnL for color scaling
    max_abs_pnl = calendar_data['pnl'].abs().max() if len(calendar_data) > 0 else 1
    
    # Build calendar with Streamlit columns instead of HTML
    import calendar as cal
    calendar_obj = cal.Calendar(firstweekday=0)
    
    # Create dict for quick lookup
    day_data = month_data.set_index('day').to_dict('index')
    
    # Header row
    day_names = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
    header_cols = st.columns(7)
    for i, day_name in enumerate(day_names):
        header_cols[i].markdown(f"**{day_name}**")
    
    # Calendar weeks
    for week in calendar_obj.monthdayscalendar(selected_year, selected_month):
        week_cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                week_cols[i].markdown("")
            else:
                info = day_data.get(day, {})
                pnl = info.get('pnl', 0)
                trades = info.get('nb_trades', 0)
                
                if trades > 0:
                    if pnl > 0:
                        emoji = "🟢"
                        pnl_str = f"+{pnl:.1f}$"
                    else:
                        emoji = "🔴"
                        pnl_str = f"{pnl:.1f}$"
                    week_cols[i].markdown(f"{emoji} **{day}**  \n{pnl_str}  \n_{trades} trades_")
                else:
                    week_cols[i].markdown(f"**{day}**")
    
    # Monthly summary
    st.markdown("---")
    st.markdown("### 📊 Résumé du mois")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("PnL Total", f"{month_data['pnl'].sum():.2f}$")
    with col2:
        st.metric("Jours Tradés", len(month_data))
    with col3:
        green_days = (month_data['pnl'] > 0).sum()
        st.metric("Jours Verts", f"{green_days}/{len(month_data)}")
    with col4:
        st.metric("Trades", int(month_data['nb_trades'].sum()))

st.markdown("---")

# ===== SECTION 2: PERFORMANCE GLOBALE =====
st.markdown('<div id="performance"></div>', unsafe_allow_html=True)
st.header("📈 3. Performance Globale")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Profit Factor", global_stats['profit_factor'])
    st.metric("Expectancy", f"{global_stats['expectancy']:.2f}$/trade")
    st.metric("Sharpe Ratio", global_stats['sharpe'])

with col2:
    st.metric("Win Rate", f"{global_stats['winrate']:.1f}%")
    st.metric("R:R Moyen", global_stats['avg_rr'])
    st.metric("Gains Totaux", f"+{global_stats['total_gains']:.2f}$")

with col3:
    st.metric("Max Drawdown", f"{global_stats['max_drawdown']:.2f}$")
    st.metric("Recovery Factor", global_stats['recovery_factor'])
    st.metric("Pertes Totales", f"-{global_stats['total_losses']:.2f}$")

st.markdown("---")

# ===== SECTION 3: DIRECTION (LONG vs SHORT) =====
st.markdown('<div id="direction"></div>', unsafe_allow_html=True)
st.header("🔀 4. LONG vs SHORT")
dir_df = format_direction_comparison(direction_stats)
st.dataframe(dir_df, width='stretch', hide_index=True)
st.markdown("---")

# ===== SECTION 4: STATS TEMPORELLES =====
st.markdown('<div id="temporal"></div>', unsafe_allow_html=True)
st.header("⏰ 5. Analyse Temporelle")

tab1, tab2, tab3 = st.tabs(["Par Heure", "Par Session", "Par Jour"])

with tab1:
    if len(hourly_stats) > 0:
        st.dataframe(hourly_stats, width='stretch', hide_index=True)
        toxic = get_toxic_hours(hourly_stats)
        profitable = get_profitable_hours(hourly_stats)
        if toxic:
            st.error(f"🚫 Heures toxiques: {', '.join(f'{h}h' for h in toxic[:5])}")
        if profitable:
            st.success(f"✅ Heures profitables: {', '.join(f'{h}h' for h in profitable[:5])}")

with tab2:
    if len(session_stats) > 0:
        st.dataframe(session_stats, width='stretch', hide_index=True)

with tab3:
    if len(daily_stats) > 0:
        st.dataframe(daily_stats, width='stretch', hide_index=True)

st.markdown("---")

# ===== SECTION 5: CLASSEMENT ACTIFS =====
st.markdown('<div id="assets"></div>', unsafe_allow_html=True)
st.header("🪙 6. Classement des Actifs")
if len(asset_stats) > 0:
    st.dataframe(
        asset_stats[['symbol', 'pnl_total', 'nb_trades', 'winrate', 'discipline_moy', 'pct_destructeurs']],
        width='stretch',
        hide_index=True
    )
st.markdown("---")

# ===== SECTION 6: STATS RISQUE =====
st.markdown('<div id="risk"></div>', unsafe_allow_html=True)
st.header("⚖️ 7. Gestion du Risque (Levier)")
col1, col2 = st.columns(2)
with col1:
    st.metric("Levier Moyen", f"{risk_stats.get('leverage_mean', 'N/A')}x")
    st.metric("Levier Max", f"{risk_stats.get('leverage_max', 'N/A')}x")
with col2:
    if len(leverage_brackets) > 0:
        st.dataframe(leverage_brackets, width='stretch', hide_index=True)
        insight = analyze_leverage_impact(df)
        st.info(insight)
st.markdown("---")

# ===== SECTION: TRADE TYPES (Stats par Setup) =====
st.markdown('<div id="tradetypes"></div>', unsafe_allow_html=True)
st.header("🎲 Trade Types (Scalp / Swing / High Lev)")

st.markdown("""
**Classification des trades:**
- **SCALP**: Durée < 5 min
- **SWING**: Durée > 60 min
- **HIGH_LEV**: Levier ≥ 50x (home run attempts)
- **STANDARD**: Autres trades
""")

# Stats par setup
if len(trade_type_stats) > 0:
    st.subheader("📊 Stats par Setup")
    st.dataframe(trade_type_stats, width='stretch', hide_index=True)
else:
    st.info("Pas assez de données pour classifier les trades")

# Stats par setup x direction
if len(trade_type_by_direction) > 0:
    st.subheader("🔀 Setup × Direction")
    st.dataframe(trade_type_by_direction, width='stretch', hide_index=True)
    
    # Insights
    best_combo = trade_type_by_direction.loc[trade_type_by_direction['PnL net ($)'].idxmax()]
    worst_combo = trade_type_by_direction.loc[trade_type_by_direction['PnL net ($)'].idxmin()]
    
    col1, col2 = st.columns(2)
    with col1:
        st.success(f"✅ Meilleur combo: **{best_combo['Setup']} {best_combo['Direction']}** (+{best_combo['PnL net ($)']:.2f}$)")
    with col2:
        st.error(f"❌ Pire combo: **{worst_combo['Setup']} {worst_combo['Direction']}** ({worst_combo['PnL net ($)']:.2f}$)")

st.markdown("---")

# ===== SECTION 7: TRADE DNA =====
st.markdown('<div id="dna"></div>', unsafe_allow_html=True)
st.header("🧬 8. Trade DNA")
if trade_dna:
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Cluster Optimal", f"#{trade_dna['cluster_id']}")
        st.metric("PnL Total", f"+{trade_dna['pnl_total']:.2f}$")
        st.metric("Win Rate", f"{trade_dna['winrate']:.1f}%")
        st.metric("Trades", trade_dna['nb_trades'])
    with col2:
        st.metric("Durée Médiane", f"{trade_dna['duree_mediane_min']:.0f} min")
        st.metric("Heure Dominante", f"{trade_dna['heure_dominante']}h")
        st.metric("Session", trade_dna['session_dominante'])
        st.metric("Direction", trade_dna['direction_dominante'])
    
    st.markdown("### 💡 Recommandations")
    for rec in dna_recommendations:
        st.success(rec)
else:
    st.warning("Impossible d'extraire le Trade DNA")
st.markdown("---")

# ===== SECTION 8: CLUSTERS =====
st.markdown('<div id="clusters"></div>', unsafe_allow_html=True)
st.header("🎯 9. Clusters Comportementaux")
if len(cluster_profiles) > 0:
    st.dataframe(cluster_profiles, width='stretch', hide_index=True)
st.markdown("---")

# ===== SECTION 9: COMPORTEMENT =====
st.markdown('<div id="behavior"></div>', unsafe_allow_html=True)
st.header("🧠 10. Patterns Comportementaux")
col1, col2 = st.columns(2)
with col1:
    st.metric("Série Wins Max", behavioral_stats.get('max_win_streak', 0))
    st.metric("Série Pertes Max", behavioral_stats.get('max_loss_streak', 0))
    st.metric("Revenge Trades", f"{behavioral_stats.get('revenge_count', 0)} ({behavioral_stats.get('revenge_pct', 0):.0f}%)")
with col2:
    st.metric("PnL Après 1 Perte", f"{behavioral_stats.get('pnl_after_1_loss', 0):.2f}$")
    st.metric("PnL Après 2 Pertes", f"{behavioral_stats.get('pnl_after_2_losses', 0):.2f}$")
    st.metric("PnL Après 3 Pertes", f"{behavioral_stats.get('pnl_after_3_losses', 0):.2f}$")

# Alertes comportementales
alerts = detect_behavioral_patterns(behavioral_stats)
if alerts:
    st.markdown("### ⚠️ Alertes")
    for alert in alerts:
        if alert['severity'] == 'HIGH':
            st.error(f"**{alert['type']}**: {alert['message']}\n{alert['impact']}")
        else:
            st.warning(f"**{alert['type']}**: {alert['message']}\n{alert['impact']}")
st.markdown("---")

# ===== SECTION 10: DURÉE =====
st.markdown('<div id="duration"></div>', unsafe_allow_html=True)
st.header("⏱️ 11. Temps en Position")
col1, col2 = st.columns(2)
with col1:
    st.metric("Durée Moyenne", f"{duration_stats.get('duration_mean', 0):.1f} min")
    st.metric("Durée Wins", f"{duration_stats.get('win_duration_median', 0):.1f} min (médiane)")
    st.metric("Durée Losses", f"{duration_stats.get('loss_duration_median', 0):.1f} min (médiane)")
with col2:
    if len(duration_brackets) > 0:
        st.dataframe(duration_brackets, width='stretch', hide_index=True)
st.markdown("---")

# ===== SECTION 11: TRADES PROBLÉMATIQUES =====
st.header("💀 12. Trades à Problème")

tab1, tab2 = st.tabs(["Trades Destructeurs", "Faux Bons Trades"])

with tab1:
    destructive = df[df['is_destructive']]
    if len(destructive) > 0:
        st.warning(f"⚠️ {len(destructive)} trades destructeurs (score < 40)")
        st.dataframe(
            destructive[['close_time', 'symbol', 'direction', 'pnl', 'discipline_score', 'duration_minutes']].head(20),
            width='stretch',
            hide_index=True
        )
    else:
        st.success("✅ Aucun trade destructeur")

with tab2:
    false_good = df[df['is_false_good']]
    if len(false_good) > 0:
        st.warning(f"⚠️ {len(false_good)} faux bons trades (gagnants mais indisciplinés)")
        st.dataframe(
            false_good[['close_time', 'symbol', 'direction', 'pnl', 'discipline_score', 'duration_minutes']].head(20),
            width='stretch',
            hide_index=True
        )
    else:
        st.success("✅ Aucun faux bon trade")

st.markdown("---")

# ===== SECTION 12: ANALYSE AVANCÉE (OPTIONNEL) =====
st.markdown('<div id="montecarlo"></div>', unsafe_allow_html=True)
st.header("🔬 13. Analyse Avancée (Monte Carlo)")

if st.button("🚀 Lancer l'analyse Monte Carlo", type="primary"):
    with st.spinner("⏳ Simulation en cours (1000 itérations)..."):
        mc_stats = monte_carlo_simulation(df, n_simulations=1000)
    
    st.success("✅ Simulation terminée")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("PnL Moyen Simulé", f"{mc_stats['mean_pnl']:.2f}$")
        st.metric("PnL Médian", f"{mc_stats['median_pnl']:.2f}$")
    with col2:
        st.metric("Intervalle 90%", f"[{mc_stats['pnl_5th']:.2f}$, {mc_stats['pnl_95th']:.2f}$]")
        st.metric("Pire Scénario", f"{mc_stats['worst_pnl']:.2f}$")
    with col3:
        st.metric("Drawdown Moyen", f"{mc_stats['mean_dd']:.2f}$")
        st.metric("Pire Drawdown", f"{mc_stats['worst_dd']:.2f}$")

st.markdown("---")

# ===== FOOTER =====
st.markdown("---")
st.markdown("*Trade Behavior Audit - Analyse comportementale sans signal de marché*")
st.markdown("*Objectif: Réduire l'overtrading, identifier ton edge, améliorer ta discipline*")
