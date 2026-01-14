# 🧠 Trade Behavior Audit

**Analyse comportementale de tes trades MEXC Futures**

Application Streamlit pour auditer tes performances de trading et identifier tes patterns comportementaux.

---

## 🚀 Installation

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
streamlit run app.py
```

Ou double-cliquer sur `launch.bat`

---

## 📊 Fonctionnalités

### Analyse Automatique
- **Auto-chargement** des fichiers MEXC (Position History + Orders)
- **42+ métriques** calculées automatiquement
- **Score de Discipline** personnalisé (0-100)

### Visualisations
| Section | Description |
|---------|-------------|
| 📈 Equity Curve | Progression du PnL dans le temps |
| 📅 Calendar Heatmap | Vue mensuelle avec 🟢/🔴 par jour |
| 🎚️ Tiltmeter | Score émotionnel temps réel |

### Statistiques
- **Performance Globale** : Profit Factor, Sharpe, Win Rate, Drawdown
- **LONG vs SHORT** : Comparaison directionnelle
- **Analyse Temporelle** : Par heure, session, jour
- **Trade Types** : Scalp / Swing / High Leverage
- **Trade DNA** : Profil de ton meilleur cluster

### Détection de Patterns
- ⚠️ **Revenge Trading** : Trade après 5+ pertes consécutives
- 💨 **Trades Impulsifs** : Moins de 5 min après le précédent
- 🚨 **Overtrading** : Plus de 10 trades/jour

---

## 📁 Structure

```
trade_behavior_audit/
├── app.py                 # Interface Streamlit principale
├── data_loader.py         # Chargement et normalisation MEXC
├── launch.bat             # Lanceur Windows
├── requirements.txt       # Dépendances Python
│
├── stats/                 # Modules de statistiques
│   ├── global_stats.py    # PnL, Profit Factor, Sharpe...
│   ├── direction_stats.py # LONG vs SHORT
│   ├── temporal_stats.py  # Par heure/session/jour
│   ├── asset_stats.py     # Par actif (BTC, ETH...)
│   ├── risk_stats.py      # Analyse du levier
│   ├── behavioral_stats.py# Détection revenge/overtrade
│   ├── duration_stats.py  # Durée des trades
│   ├── trade_types.py     # Scalp/Swing/High Lev + Tiltmeter
│   ├── visualizations.py  # Equity Curve, Heatmap
│   └── robustness.py      # Monte Carlo
│
├── ml/                    # Machine Learning
│   ├── scoring.py         # Score de discipline
│   ├── clustering.py      # Clustering KMeans
│   └── dna.py             # Extraction Trade DNA
│
└── ai/                    # Insights IA
    └── insights.py        # Génération de punchlines
```

---

## 🎯 Utilisation

### 1. Placer tes fichiers MEXC
Copie tes exports MEXC dans le dossier :
- `MEXC-Position History-*.xlsx`
- `MEXC - Historique des ordres*.xlsx`

### 2. Lancer l'app
```bash
streamlit run app.py
```

### 3. Filtrer par actif
Utilise la sidebar pour filtrer BTC, ETH, etc.

---

## 📐 Définitions Personnalisées

| Paramètre | Définition |
|-----------|------------|
| **Revenge Trade** | Trade après **5+ pertes consécutives** |
| **Scalp** | Durée < 5 minutes |
| **Swing** | Durée > 60 minutes |
| **High Leverage** | Levier ≥ 50x |
| **Trade Impulsif** | < 5 min après le précédent |

---

## 🔬 Monte Carlo

Simulation statistique qui mélange l'ordre de tes trades 1000x pour vérifier si tes résultats sont reproductibles ou dus à la chance.

---

## 📝 License

MIT - Utilisation libre

---

*Créé avec ❤️ pour les traders qui veulent s'améliorer*
