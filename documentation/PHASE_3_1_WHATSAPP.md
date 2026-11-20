# Phase 3.1 – Première connexion WhatsApp Cloud API

Cette étape ajoute le handshake GET Meta, la validation de signature POST lorsque
`WHATSAPP_APP_SECRET` est configuré, la réception des messages texte et l'envoi
d'une réponse via Graph API. Le bot réutilise le moteur de conversation local.

## 1. Variables à configurer dans `backend/.env`

```env
DEBUG=true
WHATSAPP_TOKEN=jeton_d_acces_meta
WHATSAPP_PHONE_NUMBER_ID=id_du_numero_whatsapp_cloud
WHATSAPP_VERIFY_TOKEN=une_longue_chaine_secrete_personnelle
WHATSAPP_APP_SECRET=app_secret_meta
WHATSAPP_API_VERSION=v27.0
```

Ne partagez jamais ce fichier. Ne mettez pas les valeurs secrètes dans GitHub.

## 2. Démarrer l'API

Depuis `backend` :

```powershell
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Le webhook est :
`https://VOTRE-DOMAINE-HTTPS/api/whatsapp/webhook`

Pour les essais locaux, exposez temporairement le port 8000 avec un tunnel HTTPS
(par exemple ngrok). Meta exige une URL HTTPS publique avec un certificat valide.

## 3. Configuration Meta

Dans Meta for Developers :
1. Ouvrir l'application contenant le produit WhatsApp.
2. Aller dans WhatsApp > Configuration (l'intitulé peut varier).
3. Définir l'URL de rappel ci-dessus.
4. Saisir exactement la même valeur que `WHATSAPP_VERIFY_TOKEN`.
5. Vérifier et enregistrer.
6. S'abonner au champ `messages`.

Utilisez d'abord le numéro de test fourni par Meta. Ajoutez votre téléphone comme
destinataire de test selon les instructions du tableau de bord Meta.

## 4. Limites de cette étape

- Seuls les messages texte entrants sont traités.
- Le moteur conversationnel reste basé sur des règles : l'IA générative n'est pas encore branchée.
- Les sessions et identifiants de messages traités sont en mémoire. Redémarrage ou
  plusieurs instances peuvent donc entraîner une perte d'état ou un doublon.
- La réponse est envoyée dans le contexte d'une conversation initiée par le client.
  Les messages proactifs hors fenêtre de service nécessitent des modèles approuvés.
- Le transfert humain, les pièces jointes, les boutons interactifs et la persistance
  des événements ne sont pas encore implémentés.
- `WHATSAPP_APP_SECRET` doit être renseigné en production pour exiger la signature.
  Ne déployez pas avec `DEBUG=true`.

## 5. Test de vérification sans Meta

Avec le backend lancé, ouvrir cette URL en remplaçant le jeton par la valeur de `.env` :

`http://127.0.0.1:8000/api/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=VOTRE_JETON&hub.challenge=123456`

La réponse attendue est le texte brut `123456` (HTTP 200).
Avec un jeton incorrect, la réponse doit être HTTP 403.
