"""Tests end-to-end (Phase 6) : parcours complets via l'API HTTP réelle.

Contrairement aux tests d'intégration (qui isolent un routeur avec des
adaptateurs factices pour ses dépendances lourdes), ces tests enchaînent
plusieurs appels HTTP successifs représentant un parcours utilisateur réel
(inscription -> connexion -> utilisation d'un module), avec une base de
données SQLite en mémoire réelle (pas de mock) pour la partie
authentification/rôles.
"""
