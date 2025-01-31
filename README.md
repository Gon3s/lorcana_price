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
- Min Price : Prix minimum observé
- Last Update : Date de dernière mise à jour
- Vinted Min Price : Prix minimum sur Vinted

## Utilisation

```bash
python src/main.py [options]
```

### Options

- `-s`, `--sheet-name` : Nom de l'onglet dans le Google Sheet (défaut: data)
- `-r`, `--retries` : Nombre maximum de tentatives par carte (défaut: 3)
- `-d`, `--delay` : Délai entre les tentatives en secondes (défaut: 2)
- `--sources` : Sources de prix à vérifier (cardmarket, vinted, all) (défaut: all)

### Exemples

```bash
# Utilisation avec les valeurs par défaut (toutes les sources)
python src/main.py

# Uniquement les prix Cardmarket
python src.main.py --sources cardmarket

# Uniquement les prix Vinted
python src/main.py --sources vinted

# Spécifier un autre onglet et les sources
python src/main.py --sheet-name "prix" --sources all

# Augmenter le nombre de tentatives et le délai
python src/main.py --retries 5 --delay 3
```

## Fonctionnalités
- [x] Configuration du projet
- [x] Documentation détaillée
- [x] Lecture des données depuis Google Sheets
- [x] Scraping des prix Cardmarket
- [x] Suivi historique des prix
  - Enregistrement du prix minimum observé
  - Date de dernière mise à jour des prix
  - Mise à jour uniquement si le nouveau prix est inférieur
- [ ] Scraping des prix Ebay
- [ ] Scraping des prix Leboncoin
- [ ] Scraping des prix Vinted
- [ ] Système d'alertes de prix
