# Configuration de Google Sheets API

## 1. Création et configuration du projet Google Cloud

1. Aller sur [Google Cloud Console](https://console.cloud.google.com/)
2. Créer un nouveau projet ou sélectionner un projet existant
3. Dans le menu latéral, aller dans "APIs & Services" > "Library"
4. Rechercher "Google Sheets API"
5. Cliquer sur "Enable"

## 2. Configuration du compte de service

1. Dans Google Cloud Console > "IAM & Admin" > "Service Accounts"
2. Cliquer sur "Create Service Account"
3. Remplir les informations :
   - Nom : "lorcana-price-tracker"
   - Description (optionnelle)
   - Cliquer sur "Create and Continue"
4. Pour les rôles, sélectionner :
   - Catégorie : "APIs" ou faire une recherche
   - Rôle : "Basic > Viewer" ou "Sheets API > Sheets Viewer"
   - Note : Si vous ne trouvez pas ces rôles exacts, le rôle "Viewer" basique suffira
5. Cliquer sur "Done"

## 3. Générer la clé d'accès

1. Dans la liste des comptes de service, cliquer sur celui créé
2. Aller dans l'onglet "Keys"
3. Cliquer sur "Add Key" > "Create new key"
4. Choisir le format JSON
5. Sauvegarder le fichier en tant que `service-account.json`
6. Placer le fichier à la racine du projet

## 4. Configuration du Google Sheet

1. Créer une nouvelle feuille Google Sheets
2. Structurer les colonnes comme suit :
   ```
   | Name (EN) | Name (FR) | Set | Card Number | Color | Rarity | Price | Foil Price | Cardmarket URL | Current Price | Trend Price | Avg 30 Days | Available Items | Vinted URL |
   |-----------|-----------|-----|-------------|--------|---------|--------|------------|----------------|---------------|-------------|-------------|-----------------|------------|
   | Maui...   | Maui...   | 6   | 124        | Ruby   | Legend. | 38,32 €| 45,62 €    | cardmarket/... | 35,00 €      | 37,50 €    | 36,75 €     | 42             | vinted/... |
   ```
   Notes sur les colonnes :
   - Les noms doivent être exactement comme indiqué
   - Les prix sont au format européen (virgule comme séparateur décimal)
   - Les URLs sont des chemins relatifs
   - Les colonnes de prix Cardmarket sont automatiquement mises à jour par le script
3. Cliquer sur "Share" (bouton en haut à droite)
4. Ajouter l'email du compte de service avec accès "Viewer"
   - L'email est au format : `name@project-id.iam.gserviceaccount.com`
5. Copier l'URL de la feuille

## 5. Configuration du projet

1. Copier le fichier `.env.example` vers `.env`
2. Mettre à jour le fichier `.env` :
   ```
   GOOGLE_SHEETS_URL=https://docs.google.com/spreadsheets/d/[ID]/edit
   GOOGLE_SHEETS_CREDENTIALS_FILE=service-account.json
   ```

## Notes importantes

- Le fichier `service-account.json` contient des informations sensibles et ne doit jamais être partagé ou commité
- Ajouter `service-account.json` à votre `.gitignore`
- L'URL du sheet doit être accessible par le compte de service
