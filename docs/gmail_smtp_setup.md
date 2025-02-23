# Configuration Gmail pour les notifications

## 1. Activer l'authentification à deux facteurs (2FA)

1. Aller sur [Google Account Security](https://myaccount.google.com/security)
2. Dans la section "Connexion à Google", activer "Validation en deux étapes"
3. Suivre les étapes de configuration

## 2. Créer un mot de passe d'application

1. Retourner sur [Google Account Security](https://myaccount.google.com/security)
2. Aller dans "Validation en deux étapes"
3. En bas de la page, cliquer sur "Mots de passe des applications"
4. Dans "Sélectionner une application", choisir "Autre (nom personnalisé)"
5. Nommer l'application "Lorcana Price Tracker"
6. Cliquer sur "Générer"
7. Copier le mot de passe généré (16 caractères)

## 3. Configuration du projet

1. Ouvrir le fichier `.env`
2. Mettre à jour les paramètres SMTP :
   ```
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=465
   SMTP_USERNAME=votre.email@gmail.com
   SMTP_PASSWORD=votre-mot-de-passe-application
   SMTP_FROM_EMAIL=votre.email@gmail.com
   NOTIFICATION_EMAIL=email-destination@example.com
   ```

## 4. Paramètres des notifications

Les notifications sont envoyées quand :
- Un prix Vinted est inférieur au prix Cardmarket
- La différence de prix est supérieure au pourcentage minimal configuré

Configuration du seuil de notification :
```
MIN_PRICE_DIFF_PERCENT=10  # Envoie une alerte si la différence est ≥ 10%
```

## Notes de sécurité

- Ne jamais partager ou commiter votre mot de passe d'application
- Un mot de passe d'application donne un accès limité à votre compte
- Vous pouvez révoquer l'accès à tout moment dans les paramètres de sécurité
- Il est recommandé d'utiliser un compte Gmail dédié pour l'application

## Dépannage

1. Si les emails ne sont pas envoyés :
   - Vérifier que le mot de passe d'application est correctement copié
   - S'assurer que le compte Gmail n'est pas bloqué par une politique de sécurité
   - Vérifier les logs de l'application pour les messages d'erreur

2. Si vous recevez trop de notifications :
   - Augmenter la valeur de MIN_PRICE_DIFF_PERCENT
   - Vérifier que les prix Cardmarket sont correctement mis à jour

3. Erreurs courantes :
   - "Authentication failed": Vérifier les identifiants SMTP
   - "Connection refused": Vérifier le port SMTP et le pare-feu
   - "SSL error": S'assurer que le port 465 est utilisé avec SSL
