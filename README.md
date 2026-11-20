# Ndonga_buzness

Assistant commercial WhatsApp avec tableau de bord d'administration.

## Fonctionnalités de cette version
- API FastAPI avec documentation Swagger.
- Tableau de bord React/Vite.
- Catalogue : création, modification, suppression et consultation des produits.
- Gestion des commandes et changement de statut.
- Base de données SQLite par défaut pour démarrer immédiatement.
- Configuration PostgreSQL possible via `DATABASE_URL`.
- Endpoint webhook WhatsApp et mode de démonstration local.

> Important : le projet démarre en mode local/démonstration. Les messages WhatsApp réels nécessitent un compte Meta Business, une application Meta, un numéro WhatsApp Business Platform, un jeton d'accès et la configuration du webhook. Aucun identifiant n'est inclus dans le ZIP.


## Publier le projet sur GitHub

Avant tout envoi, vérifiez que vous ne publiez aucun fichier `.env`, jeton Meta, clé API, mot de passe, base de données locale ou dossier `venv` / `node_modules`. Le fichier `.gitignore` de ce projet exclut ces éléments et conserve uniquement `backend/.env.example` comme modèle sans secrets.

**Conseil :** créez d'abord un dépôt GitHub **privé**. Ce projet est encore un MVP et sa documentation signale des éléments de sécurité à renforcer avant une exploitation commerciale publique.

Depuis PowerShell, placez-vous dans le dossier racine `Ndonga_buzness` (celui qui contient ce README), puis exécutez :

```powershell
git init -b main
git status
git add .
git status
git commit -m "Initial commit - Ndonga_buzness"
```

Avant le commit, vérifiez dans le deuxième `git status` qu'aucun `.env`, fichier `*.db`, `venv`, `node_modules` ou secret n'est listé. Si un fichier sensible apparaît, ne faites pas le commit : corrigez `.gitignore` et retirez-le de l'index avec `git rm --cached NOM_DU_FICHIER`.

Créez ensuite un dépôt vide sur https://github.com/new : nom `Ndonga_buzness`, visibilité **Private**, et ne cochez pas les options de création automatique d'un README, d'un `.gitignore` ou d'une licence (ils sont déjà présents localement). Puis reliez et envoyez le dépôt :

```powershell
git remote add origin https://github.com/VOTRE-PSEUDO/Ndonga_buzness.git
git remote -v
git push -u origin main
```

Remplacez `VOTRE-PSEUDO` par votre identifiant GitHub. GitHub vous demandera de vous authentifier si nécessaire. Ne mettez jamais votre mot de passe ou un jeton d'accès directement dans une commande ou dans un fichier du projet.

Après l'envoi, actualisez la page du dépôt GitHub et vérifiez que les dossiers `backend`, `frontend` et `documentation` ainsi que ce README sont visibles.

Pour les mises à jour futures :

```powershell
git add .
git status
git commit -m "Description des modifications"
git push
```

## Prérequis
- Python 3.10 ou plus récent
- Node.js LTS et npm
- PostgreSQL facultatif (SQLite est utilisé par défaut)

## 1. Démarrer le backend (Windows PowerShell)

Ouvrir un terminal dans le dossier `backend` :

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

API : http://127.0.0.1:8000  
Documentation : http://127.0.0.1:8000/docs

Si PowerShell bloque l'activation :
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

## 2. Démarrer le frontend

Ouvrir un deuxième terminal dans `frontend` :

```powershell
npm install
npm run dev
```

Ouvrir l'adresse indiquée par Vite, généralement http://localhost:5173.

## 3. Utiliser PostgreSQL

Créer une base `ndonga_buzness_db`, puis modifier `backend/.env` :

```env
DATABASE_URL=postgresql+psycopg://postgres:VOTRE_MOT_DE_PASSE@localhost:5432/ndonga_buzness_db
```

Redémarrer le backend. Les tables sont créées automatiquement au démarrage.

## 4. WhatsApp Cloud API

Les paramètres suivants sont prévus dans `backend/.env` :
- `WHATSAPP_TOKEN`
- `WHATSAPP_PHONE_NUMBER_ID`
- `WHATSAPP_VERIFY_TOKEN`
- `WHATSAPP_APP_SECRET`
- `WHATSAPP_API_VERSION`

Le webhook de vérification GET est disponible sur `/api/whatsapp/webhook`.
Le traitement POST de base accepte les notifications Meta et journalise les événements.
Le mode démo du tableau de bord ne transmet pas de messages WhatsApp réels.

Documentation officielle : https://developers.facebook.com/docs/whatsapp/cloud-api/

## 5. Limites et sécurité avant production
Cette base est un MVP de démarrage, pas encore une plateforme prête pour un déploiement commercial public.
Avant production, ajouter notamment : authentification administrateur, gestion des rôles, validation renforcée, protection contre les abus, journalisation, sauvegardes, tests automatisés, gestion des consentements et vérification de signature des webhooks Meta.
Ne jamais publier le fichier `.env` ni partager les jetons d'accès.

## Phase 2.1 – Simulateur conversationnel
Une page **Tester le BOT** est maintenant disponible dans le tableau de bord. Elle permet de tester localement : accueil, catalogue, tarifs, commande guidée et réponses de suivi simples.

- API de simulation : `POST /api/chat/simulate`
- Réinitialisation de session : `POST /api/chat/reset`
- Corps attendu : `{"session_id":"demo-1","message":"Bonjour"}`

La simulation crée une vraie commande locale et décrémente le stock à la fin du parcours. Utilisez donc des données de test. Les sessions sont conservées en mémoire du processus : elles sont perdues au redémarrage du backend. Le moteur actuel est un moteur d'intentions/règles déterministe, prêt à recevoir un fournisseur IA dans une prochaine étape ; il ne faut pas encore le présenter comme une IA générative connectée.


## Phase 3.1 – Connexion WhatsApp Cloud API
Consultez `documentation/PHASE_3_1_WHATSAPP.md`. Le webhook GET/POST traite les messages texte entrants et répond via l'API Graph lorsque les identifiants Meta sont configurés. La connexion réelle nécessite une URL HTTPS publique, un jeton Meta, un Phone Number ID, un App Secret et l'abonnement au champ `messages`.
