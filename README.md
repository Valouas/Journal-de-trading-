# 🃏 Trade Behavior Audit  
### Un miroir pour les traders lucides (en developpement)

> Le marché ne te combat pas.  
> Tes habitudes, si.

---

## Ce que c’est

Ce n’est **pas** un bot de trading.  
Ce n’est **pas** une stratégie.  
Ce n’est **pas** un générateur de signaux.

C’est un **outil d’audit comportemental** basé sur **l’analyse complète et honnête** de ton historique de trades.

Il ne cherche pas l’erreur.  
Il cherche **la vérité**.

---

## Ce que fait le bot

Le bot analyse **toutes tes positions**, sans biais ni narration, et met en évidence :

- Performance globale et par direction (LONG / SHORT)
- PnL, drawdown, expectancy, profit factor
- Distribution des gains et des pertes
- Timing des trades (heure, session, durée)
- Patterns de répétition
- Discipline et gestion du risque
- Trades destructeurs et faux bons trades
- Dégradation comportementale après pertes
- Revenge trading, overtrading, impatience
- Ton **edge réel**, pas celui que tu racontes

Les points forts sont identifiés.  
Les points faibles sont exposés.  
Aucune complaisance, aucune attaque.

---

## Principe central

La plupart des traders perdent de l’argent  
non pas parce qu’ils ne savent pas trader,  
mais parce qu’ils **n’appliquent pas ce qui fonctionne pour eux**.

Ce bot existe pour isoler :
- ce qui te fait gagner
- ce qui te fait perdre
- et ce que tu continues de faire malgré les preuves

---

## Résultat

Le bot produit :

- Un résumé brutal mais factuel
- Une analyse comportementale complète
- Des alertes quand le comportement devient destructeur
- Un profil de trading cohérent (direction, durée, timing)
- Un “ADN de trade” basé sur tes données réelles
- Des recommandations simples et hiérarchisées

Ce n’est pas un jugement.  
C’est un constat.

---

## Ce que ce bot ne fera pas

- ❌ Prédire le marché
- ❌ Te dire quand entrer ou sortir
- ❌ Te protéger de toi-même
- ❌ Transformer un mauvais trader en bon trader

Il te montre **exactement** ce que tu fais.  
À toi d’assumer la suite.

---

## À qui s’adresse ce projet

- Traders déjà actifs
- Traders qui ont des données
- Traders fatigués des indicateurs magiques
- Personnes qui préfèrent la clarté au confort

Si tu cherches des excuses, ce bot n’en fournit aucune.  
Si tu cherches de la lucidité, il est là.

---

## Philosophie

Aucun signal.  
Aucune promesse.  
Aucune illusion.

Uniquement :
- des faits
- des chiffres
- du comportement

---

## Licence

Usage **non commercial uniquement**.

Tu peux :
- utiliser
- étudier
- modifier

Tu ne peux pas :
- vendre
- redistribuer comme produit payant
- t’approprier ce travail

Voir le fichier `LICENSE`.

---

## Note finale

Ce bot ne te rendra pas meilleur.

Il t’expliquera **pourquoi tu l’es parfois**  
et **pourquoi tu ne l’es pas le reste du temps**.

Le marché n’a rien à prouver.  
Toi, si.


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
