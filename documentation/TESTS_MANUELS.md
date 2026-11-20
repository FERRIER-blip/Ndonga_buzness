# Tests manuels de démarrage

1. Lancer le backend et ouvrir `/docs`.
2. Appeler `GET /api/health` : réponse attendue `healthy`.
3. Appeler `GET /api/products` : trois produits de démonstration apparaissent au premier lancement.
4. Créer un produit avec `POST /api/products`.
5. Créer une commande avec `POST /api/orders` en utilisant un identifiant produit existant.
6. Vérifier la commande avec `GET /api/orders`.
7. Modifier son statut avec `PATCH /api/orders/{id}/status`.
8. Ouvrir le frontend et vérifier les vues Vue générale, Produits et Commandes.

Les données sont stockées dans `backend/ndonga_buzness.db` si SQLite est utilisé.
