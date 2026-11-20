# Déposer Ndonga_buzness sur GitHub (Windows / PowerShell)

## Avant de commencer

- Installer Git : https://git-scm.com/download/win
- Créer ou utiliser un compte : https://github.com/
- Décompresser l'archive, puis ouvrir dans VS Code le dossier `Ndonga_buzness` qui contient le présent guide et le README.
- Garder le dépôt privé au début.

## Vérifier les fichiers à ne pas publier

Ne jamais publier :
- `backend/.env` ou tout autre `.env` contenant des identifiants ;
- jeton WhatsApp/Meta, App Secret, clé d'IA, mot de passe PostgreSQL ;
- fichiers de base locale `*.db`, `*.sqlite`, `*.sqlite3` ;
- `venv`, `.venv`, `node_modules`, `dist`.

Le `.gitignore` à la racine est prévu pour ignorer ces fichiers. Le fichier `backend/.env.example` est un modèle et peut être publié s'il ne contient que des valeurs fictives.

## 1. Vérifier Git

Dans le terminal VS Code :

```powershell
git --version
```

Si Git n'est pas reconnu, installez-le puis redémarrez VS Code.

## 2. Initialiser le dépôt local

Assurez-vous d'être à la racine `Ndonga_buzness` :

```powershell
pwd
dir
git init -b main
git status
```

La commande `dir` doit afficher `backend`, `frontend`, `documentation`, `README.md` et `.gitignore`.

## 3. Préparer le premier commit

```powershell
git add .
git status
```

Lisez la liste des fichiers sous « Changes to be committed ». Aucun `.env` réel, fichier de base de données, jeton, `venv` ou `node_modules` ne doit apparaître. Si c'est le cas, arrêtez-vous et corrigez `.gitignore` avant de continuer.

Puis :

```powershell
git commit -m "Initial commit - Ndonga_buzness"
```

Si Git demande votre identité :

```powershell
git config --global user.name "Votre nom GitHub"
git config --global user.email "votre-email-associe-a-github@example.com"
```

Relancez ensuite la commande `git commit`.

## 4. Créer le dépôt distant

1. Ouvrir https://github.com/new et se connecter.
2. Repository name : `Ndonga_buzness`.
3. Description : `Assistant commercial WhatsApp et tableau de bord de gestion`.
4. Choisir **Private** pour le moment.
5. Ne pas cocher « Add a README », « Add .gitignore » ou « Choose a license » : ces fichiers existent déjà localement.
6. Cliquer sur **Create repository**.

## 5. Relier le projet et envoyer les fichiers

Copiez l'adresse HTTPS du dépôt nouvellement créé, puis remplacez `VOTRE-PSEUDO` ci-dessous par votre identifiant GitHub :

```powershell
git remote add origin https://github.com/VOTRE-PSEUDO/Ndonga_buzness.git
git remote -v
git push -u origin main
```

Suivez la fenêtre de connexion GitHub si elle apparaît. N'inscrivez jamais un mot de passe ou un token dans l'URL.

## 6. Vérifier

Rechargez la page du dépôt GitHub. Les dossiers et fichiers du projet doivent apparaître. Vérifiez également qu'aucun `.env`, base locale ou fichier secret n'a été envoyé.

## 7. Envoyer les modifications futures

Après chaque modification du code :

```powershell
git add .
git status
git commit -m "Décrire la modification"
git push
```

## Attention

Si un secret a déjà été commité ou envoyé sur GitHub, le supprimer du dernier dossier ne suffit pas : il faut révoquer/renouveler le secret concerné et traiter son historique Git. Pour ce MVP, gardez le dépôt privé et ne déployez pas publiquement avant d'avoir renforcé l'authentification, les permissions, les sauvegardes et les protections du webhook.
