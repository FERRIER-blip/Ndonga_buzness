# Cahier des charges – Ndonga_buzness

## Objectif
Automatiser le service commercial d'une entreprise de commerce via WhatsApp.

## Utilisateurs
- Client : consulte les produits, demande des informations et passe commande.
- Administrateur : gère le catalogue, les stocks et les commandes.
- Conseiller : reprend manuellement les demandes qui nécessitent une intervention humaine (fonction à finaliser).

## Modules MVP
1. Catalogue produits et catégories.
2. Gestion des stocks.
3. Création et suivi des commandes.
4. Tableau de bord et indicateurs.
5. Préparation de l'intégration WhatsApp Cloud API.
6. Automatisation conversationnelle à compléter et relier au webhook.

## Règles métier
- Les prix sont exprimés en FCFA dans l'interface.
- Une commande possède un numéro unique.
- Une commande ne peut pas être créée si le produit est inactif ou si le stock est insuffisant.
- Le stock est décrémenté lors de la création de commande.
- Les statuts sont : En attente, Confirmée, En préparation, Expédiée, Terminée, Annulée.

## Hors périmètre de cette première livraison
- Paiement en ligne réel.
- Envoi et réception WhatsApp réels.
- IA conversationnelle connectée à une base de connaissances.
- Authentification et gestion des rôles de production.
- Déploiement public.
