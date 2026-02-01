# Contribution Guidelines

## Workflow de développement

Ce projet utilise un workflow **Feature Branch** pour assurer la qualité et la traçabilité du code. Tous les changements passent par une revue de code avant d'être fusionnés à la branche principale.

### Règles obligatoires

1. **Ne jamais pousser directement sur `main`**
   - La branche `main` est la branche de production
   - Tous les changements doivent passer par une Pull Request (PR)

2. **Force push et suppression interdits**
   - Les force push (`git push --force`) sont interdits sur toutes les branches
   - Les branches ne doivent pas être supprimées sans validation

3. **Chaque modification = une branche feature**
   - Créer une nouvelle branche pour chaque feature/correction
   - Nommer les branches de manière descriptive : `feature/nom-court`, `fix/description`, `refactor/objectif`

### Processus de développement

#### Étape 1 : Créer une branche feature
```bash
git checkout main
git pull origin main
git checkout -b feature/description-courte
```

#### Étape 2 : Développer et commiter
```bash
git add .
git commit -m "Description claire du changement"
```

Utiliser des messages de commit explicites :
- Format : `Type: Description` (ex: `Feature: Ajouter validation email`, `Fix: Corriger bug affichage`, `Docs: Mettre à jour README`)
- Types acceptés : `Feature`, `Fix`, `Refactor`, `Docs`, `Test`, `Chore`

#### Étape 3 : Pousser la branche
```bash
git push -u origin feature/description-courte
```

#### Étape 4 : Créer une Pull Request
1. Aller sur https://github.com/jewandji/gestion-etudiants
2. Créer une PR depuis la branche feature vers `main`
3. Remplir le titre et la description (utiliser le template si disponible)

**Éléments obligatoires dans la description :**
- Résumé des changements
- Impact fonctionnel
- Tests effectués
- Checklist :
  - [ ] Code testé localement
  - [ ] Pas de warnings/erreurs
  - [ ] Documentation mise à jour (si applicable)

#### Étape 5 : Revue et merge
- Au moins une revue requise avant merge
- Résoudre les commentaires et suggestions
- Merger une fois approuvé
- Supprimer la branche après merge

### Exemple complet

```bash
# Créer une branche
git checkout -b feature/ajouter-validation-email

# Faire des modifications et commits
echo "validation" >> app.py
git add app.py
git commit -m "Feature: Ajouter validation email robuste"

# Pousser
git push -u origin feature/ajouter-validation-email

# [Sur GitHub] Créer la PR, ajouter description, attendre review
# [Après approbation] Merger via interface GitHub
# [Localement] Nettoyer
git checkout main
git pull origin main
git branch -d feature/ajouter-validation-email
```

## Bonnes pratiques

### Commits
- Commits atomiques (un changement logique par commit)
- Messages descriptifs et concis
- Éviter les commits "WIP" ou "fix"

### Branches
- Une branche par feature/fix (une responsabilité unique)
- Branche à jour avec `main` avant de créer la PR
- Nettoyer les branches locales régulièrement : `git branch -d branche-terminée`

### Pull Requests
- Une PR = une feature/fix (logiquement indépendante)
- Description claire et précise
- Taille raisonnable (idéalement < 400 lignes)
- Tests inclus pour les nouvelles features

## Protection du code

La branche `main` est protégée par le processus suivant :
- Pas de push direct autorisé
- Toutes les PR sont revisitées avant merge
- Les développeurs appliquent manuellement les blocages de force push
- L'intégrité de l'historique est garantie par la discipline du workflow

## Aide et questions

Pour toute question sur ce workflow :
1. Consulter la documentation GitHub : https://docs.github.com/en/get-started/quickstart/contributing-to-projects
2. Demander aux mainteneurs du projet

---

**Version:** 1.0  
**Dernière mise à jour:** 2026-02-01  
**Statut:** Effectif
