# Phase 2.1 – Moteur conversationnel local

## Objectif
Tester le parcours client sans dépendre immédiatement de WhatsApp Cloud API.

## Scénarios pris en charge
- Accueil : bonjour, bonsoir, salut, MENU.
- Catalogue et tarifs : PRODUITS, CATALOGUE, PRIX, TARIFS.
- Questions simples sur un produit dont le nom est dans le catalogue.
- Commande guidée : choix du produit, quantité, nom, téléphone.
- Création d'une commande dans la base et décrémentation du stock.
- Demande de suivi et prise en charge de la demande de conseiller (transfert humain réel à ajouter).

## Tester depuis Swagger
1. Démarrer le backend.
2. Ouvrir `http://127.0.0.1:8000/docs`.
3. Repérer `Assistant conversationnel` puis `POST /api/chat/simulate`.
4. Envoyer successivement les messages ci-dessous avec le même `session_id` :

```json
{"session_id":"essai-01","message":"Bonjour"}
```
```json
{"session_id":"essai-01","message":"Commander"}
```
Puis répondre au bot avec le nom exact d'un produit actif, une quantité, un nom client et un numéro de test.

## Limites connues
- Sessions stockées en mémoire : redémarrage du backend = perte des conversations en cours.
- Reconnaissance basée sur règles et mots-clés ; aucune IA générative n'est encore branchée.
- Le suivi par numéro est une première version.
- Pas encore de transfert humain ni d'envoi WhatsApp réel.
- Avant production : persistance des sessions, contrôle de concurrence du stock, authentification, validation du webhook Meta et tests automatisés.
