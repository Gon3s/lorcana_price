# Lorcana Price Tracker

Un outil pour suivre les prix des cartes Lorcana sur différentes plateformes.

## Configuration

### Prérequis
- Python 3.10+
- Un compte Google Cloud Platform
- Une feuille Google Sheets contenant la liste des cartes

### Installation

1. Cloner le repository
```bash
git clone <repository-url>
cd lorcana_price
```

2. Installer les dépendances
```bash
pip install -r requirements.txt
```

3. Configuration de l'environnement
- Suivre les instructions dans `docs/google_sheets_setup.md`
- Copier le fichier `.env.example` vers `.env`
- Configurer les variables d'environnement

### Structure du Google Sheet
Le Google Sheet doit contenir les colonnes suivantes :
- Name (EN) : Nom de la carte en anglais
- Name (FR) : Nom de la carte en français
- Set : Numéro du set
- Card Number : Numéro de la carte
- Color : Couleur de la carte
- Rarity : Rareté de la carte
- Price : Prix normal en euros
- Foil Price : Prix foil en euros
- Cardmarket URL : URL relative de la carte sur Cardmarket
- Current Price : Prix actuel sur Cardmarket
- Trend Price : Prix tendance sur Cardmarket
- Avg 30 Days : Prix moyen sur 30 jours
- Available Items : Nombre d'articles disponibles
- Vinted URL : URL relative de la carte sur Vinted

## Utilisation

```bash
python src/main.py
```

## Fonctionnalités
- [x] Configuration du projet
- [x] Documentation détaillée
- [x] Lecture des données depuis Google Sheets
- [x] Scraping des prix Cardmarket
- [ ] Scraping des prix Vinted
- [ ] Scraping des prix Ebay
- [ ] Scraping des prix Leboncoin
- [ ] Système d'alertes de prix
