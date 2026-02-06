# Guide d'utilisation - Nouvelles fonctionnalités

## 📅 Calendrier dynamique pour les dates

### Où utiliser le calendrier ?

Le calendrier graphique est disponible dans les champs de date suivants :

#### 1. Ajout d'étudiant - Date de naissance
- **Localisation** : Onglet "Étudiants" → Formulaire "Ajouter un étudiant"
- **Champ** : "Date naissance"

#### 2. Semestres - Dates de début et fin
- **Localisation** : Onglet "Calendrier" → Section "Semestres"
- **Champs** : "Début" et "Fin"

#### 3. Périodes - Dates de début et fin
- **Localisation** : Onglet "Calendrier" → Section "Périodes"
- **Champs** : "Début" et "Fin"

### Comment utiliser le calendrier ?

#### Méthode 1 : Sélection graphique (recommandée)
```
1. Cliquez sur le bouton 📅 à droite du champ de date
2. Un calendrier s'affiche
3. Naviguez jusqu'au mois/année souhaité(e)
4. Cliquez sur le jour
5. Cliquez "OK"
6. La date s'affiche automatiquement au format YYYY-MM-DD
```

#### Méthode 2 : Saisie manuelle
```
1. Cliquez directement dans le champ de texte
2. Tapez la date au format YYYY-MM-DD
3. Exemple : 2026-02-02 (02 février 2026)
4. Appuyez sur Entrée
```

### Format de date accepté

- **Format** : `YYYY-MM-DD`
- **Y** : Année (4 chiffres)
- **M** : Mois (2 chiffres, 01-12)
- **D** : Jour (2 chiffres, 01-31)

**Exemples valides** :
- ✅ 2026-02-02 (2 février 2026)
- ✅ 1995-12-25 (25 décembre 1995)
- ✅ 2020-01-01 (1er janvier 2020)

**Exemples invalides** :
- ❌ 02/02/2026 (format américain)
- ❌ 02-02-2026 (tirets mal placés)
- ❌ 26-02-02 (ordre incorrect)

### Installation du calendrier graphique (tkcalendar)

Si vous souhaitez utiliser l'interface calendrier graphique complète :

```bash
# Installer tkcalendar
pip install tkcalendar

# Redémarrer l'application
python gestion_etudiants/main.py
```

Après installation, le bouton 📅 ouvrira un véritable calendrier interactif.

---

## 📅 Liste déroulante d'années

### Où utiliser la liste d'années ?

#### Inscriptions - Année académique
- **Localisation** : Onglet "Inscriptions" → Formulaire "Nouvelle inscription"
- **Champ** : "Année académique"

### Comment utiliser la liste d'années ?

```
1. Cliquez sur la flèche déroulante du champ
2. La liste s'affiche avec les années en ordre décroissant
3. Sélectionnez l'année désirée (ex: 2026)
4. La sélection s'affiche dans le champ
```

### Plage d'années disponibles

- **De** : 2026 (année actuelle)
- **À** : 1980 (ou l'année définie)
- **Ordre** : Décroissant (années récentes d'abord)

### Avantages

✅ Pas de risque d'erreur de saisie  
✅ Sélection rapide des années courantes  
✅ Interface cohérente avec le système  
✅ Prévient les formats invalides

---

## 🎯 Bonne pratique pour les inscriptions

Pour créer une inscription sans erreur FOREIGN KEY :

```
1. Sélectionner un ÉTUDIANT valide (doit exister dans la base)
2. Sélectionner une FILIÈRE valide
3. Sélectionner un NIVEAU valide
4. Sélectionner un GROUPE valide (les groupes existants s'affichent)
5. Sélectionner une ANNÉE ACADÉMIQUE dans la liste
6. Cliquer "Enregistrer inscription"
```

### Dépannage

**Erreur : "Étudiant, filière, niveau et année sont obligatoires"**
- Assurez-vous de bien sélectionner chaque champ
- Les listes déroulantes doivent avoir une sélection

**Erreur : "FOREIGN KEY constraint failed"** (ancien problème)
- ✅ Ce problème a été résolu
- Le groupe est maintenant correctement validé

---

## 📝 Changements dans le formulaire étudiant

### Suppression du champ "Lieu naissance"

Le champ "Lieu naissance" a été supprimé pour simplifier le formulaire.

**Avant** : 5 champs académiques
- Date naissance
- Lieu naissance ← **SUPPRIMÉ**
- Sexe
- Pays

**Après** : 4 champs académiques
- Date naissance
- Sexe
- Pays de naissance ← **RENOMMÉ**

### Renommage : "Pays" → "Pays de naissance"

Le champ "Pays" a été renommé en "Pays de naissance" pour plus de clarté.

**Recherche dynamique activée** :
```
1. Commencez à taper le nom du pays
2. La liste se filtre automatiquement
3. Sélectionnez le pays dans la liste
```

**Pays disponibles** : Plus de 200 pays du monde entier

---

## 📊 Semestres complets (S01 à S10)

### Nouvelle gamme de semestres

La liste des semestres a été étendue pour couvrir tous les semestres :

**Semestres disponibles** :
- **S01** à **S06** : Nouveaux semestres ajoutés
- **S07** à **S10** : Semestres existants

### Utilisation

**Dans "Modules & Notes"** :
```
1. Cliquer "Ajouter module"
2. Sélectionner le semestre (S01-S10)
3. Remplir les autres champs
4. Cliquer "Ajouter module"
```

### Cas d'utilisation

- **S01-S06** : Formations courtes, programmes personnalisés
- **S07-S10** : Programmes standards 2 ans (MSc1 CSDS)

---

## 🔧 Dépannage

### Le bouton 📅 ne fonctionne pas

**Solution** :
```bash
# Installer tkcalendar
pip install tkcalendar

# Redémarrer l'application
python gestion_etudiants/main.py
```

### Le calendrier affiche un avertissement

**Message** : "Installez tkcalendar: pip install tkcalendar"

**Solution** : Suivez les instructions dans le message

### Je ne vois pas la liste d'années

**Cause** : Vous n'êtes pas dans le bon formulaire

**Vérification** :
- Allez à "Inscriptions"
- Cherchez le champ "Année académique"
- Cliquez sur la flèche déroulante

### Je ne peux pas sélectionner le groupe

**Cause possible** : Aucun groupe n'existe dans la base de données

**Solution** :
1. Créer des groupes d'abord (si nécessaire)
2. Les groupes doivent être créés dans la gestion des groupes
3. Ils apparaîtront automatiquement dans la liste

---

## 📞 Support

Pour toute question ou problème :

1. Consultez la documentation [MODIFICATIONS.md](MODIFICATIONS.md)
2. Vérifiez la [checklist](CHECKLIST.md)
3. Consultez le guide d'installation [INSTALLATION_OPTIONNELLE.md](INSTALLATION_OPTIONNELLE.md)

---

**Dernière mise à jour** : 02 février 2026  
**Version** : 1.x  
**Langue** : Français
