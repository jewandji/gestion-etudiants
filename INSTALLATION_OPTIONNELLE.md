# Installation des dépendances optionnelles

## Calendrier dynamique (tkcalendar)

Pour bénéficier des sélecteurs de calendrier dynamiques dans les champs de date, vous devez installer la bibliothèque `tkcalendar` :

### Installation

```bash
pip install tkcalendar
```

### Après installation

Une fois installée, vous pourrez :
- ✅ Cliquer sur le bouton 📅 dans les champs de date
- ✅ Sélectionner des dates via un calendrier graphique
- ✅ Éviter les erreurs de format YYYY-MM-DD

### Champs concernés

Les sélecteurs de calendrier sont disponibles pour :
- **Date naissance** : Formulaire "Ajouter un étudiant"
- **Début/Fin semestre** : Formulaire "Semestres"
- **Début/Fin période** : Formulaire "Périodes"

### Comportement sans tkcalendar

Si `tkcalendar` n'est pas installé :
- ⚠️ Un message d'avertissement s'affiche au clic sur 📅
- ℹ️ Vous pouvez continuer à saisir les dates manuellement
- 📝 Format requis : YYYY-MM-DD (ex: 2026-02-02)

## Autres dépendances requises

Les dépendances suivantes sont déjà listées dans `requirements.txt` et sont nécessaires :

```bash
pip install -r requirements.txt
```

Cela installe :
- ttkbootstrap (interface graphique améliorée)
- reportlab (génération PDF)
- openpyxl (export Excel)
- matplotlib (graphiques)

## Version Python

- **Minimum** : Python 3.7
- **Recommandée** : Python 3.8+

## Vérifier l'installation

```python
# Vérifier que tkcalendar est installé
python -c "import tkcalendar; print('✓ tkcalendar est installé')"

# Vérifier la version
python -c "import tkcalendar; print(tkcalendar.__version__)"
```

## Support

En cas de problème d'installation de `tkcalendar` :

1. Vérifiez que vous utilisez le bon environnement Python
2. Essayez une réinstallation :
   ```bash
   pip uninstall tkcalendar
   pip install --upgrade tkcalendar
   ```
3. L'application continue de fonctionner sans tkcalendar (saisie manuelle)
