# Prediction Engine Architecture

Ce dossier contient le moteur de calcul de probabilités de victoire pour l'OL Match Analyzer.

## Structure

### 📂 Racine (`prediction_engine/`)

- **`build_match_probabilities.py`** : Script principal. Orchestre le chargement des données, le calcul des probabilités et la génération des prédictions.
- **`config.py`** : Fichier de configuration. Contient les pondérations du modèle (poids des blessures, avantage domicile, forme récente, etc.) pour garantir un modèle "White Box".
- **`data_loader.py`** : Gestionnaire de données. Charge les CSV existants (lecture seule) et initialise les nouveaux CSV du moteur de prédiction.

### 📂 Scraping (`prediction_engine/scraping/`)

Contient les scripts dédiés à la récupération de nouvelles données spécifiques au moteur de prédiction.

- **`scrape_manager_h2h.py`** : Scrape l'historique des confrontations entre entraîneurs.
- **`scrape_stadiums.py`** : Scrape les données des stades (capacité, affluence moyenne) pour le calcul de l'avantage domicile.

### 📂 Data (`prediction_engine/data/`)

Stockage des fichiers CSV générés par le moteur. Ne contient que des nouveaux fichiers, jamais de fichiers écrasés du projet principal.

- **`matches_database.csv`** : Base consolidée des matchs pour l'analyse.
- **`manager_h2h.csv`** : Base de données des confrontations entraîneurs.
- **`stadiums.csv`** : Données des stades.
- **`match_predictions.csv`** : Sortie finale des prédictions.

## Principes

1. **Non-destructif** : Aucune donnée existante du dossier parent `data/processed` n'est modifiée.
2. **Explicabilité** : Tous les coefficients sont définis dans `config.py`.
3. **Modularité** : Chaque script a une responsabilité unique.
