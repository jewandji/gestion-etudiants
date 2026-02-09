# Application de Gestion des Étudiants

**Référence :** ESILV\Projets\Python | MACSIN4A0425  
**Date de mise à jour :** 31/01/2026  
**Auteurs :** Yobe GNADAME, Mileina Malou, Jean-Eudes Wandji

---

## Sommaire

1. [Introduction](#introduction)
2. [Présentation du projet et objectifs](#présentation-du-projet-et-objectifs)
3. [Analyse des besoins fonctionnels](#analyse-des-besoins-fonctionnels)
4. [Choix techniques et architecture](#choix-techniques-et-architecture-de-lapplication)
5. [Conception de la base de données](#conception-de-la-base-de-données)
6. [Fonctionnalités principales](#fonctionnalités-principales-de-lapplication)
7. [Limites et perspectives d'amélioration](#limites-et-perspectives-damélioration)
8. [Conclusion](#conclusion)

---

## Introduction

La gestion des données académiques constitue un enjeu central pour les établissements d'enseignement supérieur. Le suivi des étudiants, des inscriptions, des résultats, des absences et des structures pédagogiques nécessite des outils fiables, cohérents et faciles à utiliser. Lorsque ces informations sont gérées de manière manuelle ou à l'aide de solutions fragmentées, le risque d'erreurs augmente et le travail administratif devient rapidement lourd et inefficace.

Dans ce contexte, ce projet a pour objectif de concevoir une application desktop permettant de centraliser et structurer l'ensemble des données liées au parcours académique des étudiants. L'application vise à accompagner les acteurs pédagogiques et administratifs dans leurs tâches quotidiennes, tout en offrant une vision claire et globale de la situation académique.

Développée en Python, l'application propose des fonctionnalités essentielles telles que la gestion des étudiants et des inscriptions, le suivi des notes et des absences, la génération de documents officiels, ainsi que l'analyse des données à travers des indicateurs et tableaux de bord. Une attention particulière a également été portée à la sécurité et à l'intégrité des données, notamment par l'utilisation d'une base de données centralisée et d'un système d'authentification.

Ce projet s'inscrit ainsi dans une démarche pragmatique visant à répondre à des besoins concrets, tout en mettant en pratique les compétences techniques acquises au cours de la formation.

---

## Présentation du projet et objectifs

Le projet consiste à développer une application desktop dédiée à la gestion académique des étudiants au sein d'un établissement d'enseignement supérieur. L'objectif principal est de regrouper, dans un outil unique, l'ensemble des informations nécessaires au suivi du parcours universitaire des étudiants, depuis leur inscription jusqu'à l'analyse de leurs résultats et de leur assiduité.

L'application a été pensée pour répondre à des besoins concrets rencontrés dans la gestion quotidienne :
- Enregistrer et consulter les informations des étudiants
- Organiser les structures académiques (filières, niveaux, modules, enseignants)
- Saisir et exploiter les notes
- Suivre les absences
- Produire des documents officiels (relevés de notes, attestations de scolarité)

Au-delà des fonctionnalités de gestion, le projet vise également à faciliter l'analyse des données académiques. Des calculs automatiques (moyennes, taux d'absences) et des tableaux de bord permettent d'avoir une vision synthétique de la situation globale et d'identifier rapidement les cas nécessitant une attention particulière.

Enfin, un objectif important du projet est la fiabilité et la sécurité des données. Pour cela, l'application s'appuie sur une base de données SQLite centralisée, des contraintes d'intégrité et un système d'authentification garantissant un accès contrôlé aux fonctionnalités.

---

## Analyse des besoins fonctionnels

L'application doit répondre à des besoins fonctionnels précis liés à la gestion académique des étudiants. Ces besoins ont été identifiés à partir des tâches couramment réalisées par les services administratifs et pédagogiques.

**Gestion complète des étudiants**  
L'application doit permettre l'enregistrement des informations personnelles, la génération d'un matricule unique, la consultation rapide des dossiers et l'accès à une fiche détaillée regroupant l'ensemble du parcours académique.

**Structuration académique**  
L'application doit permettre de gérer les filières, les niveaux et les modules, ainsi que l'affectation des enseignants aux enseignements. Cette organisation est nécessaire pour garantir la cohérence des inscriptions et des évaluations.

**Gestion des inscriptions**  
Le système doit enregistrer les inscriptions des étudiants par année académique, filière et niveau, tout en conservant un historique fiable du parcours universitaire.

**Gestion des notes**  
Le système doit permettre la saisie, la consultation et la modification des résultats, avec un contrôle des valeurs et un calcul automatique des moyennes. Toute modification doit être tracée afin d'assurer la transparence et la fiabilité des données.

**Suivi de l'assiduité et des absences**  
L'application doit permettre d'enregistrer les absences, de gérer les justificatifs et de déclencher des alertes lorsque certains seuils sont dépassés.

**Génération de documents et analyses**  
L'application doit offrir des fonctionnalités de génération de documents (relevés de notes, attestations) ainsi que des outils d'analyse et de visualisation sous forme de statistiques et de tableaux de bord, afin d'aider à la prise de décision.

---

## Choix techniques et architecture de l'application

Le développement de l'application a été réalisé en **Python**, un langage adapté à la création d'outils de gestion grâce à sa simplicité, sa lisibilité et la richesse de son écosystème. Ce choix permet de maintenir un code clair, évolutif et facilement compréhensible.

### Stack technique

| Composant | Technologie | Justification |
|-----------|-------------|--------------|
| **Langage** | Python 3.x | Simplicité, lisibilité, écosystème riche |
| **Interface** | Tkinter + ttkbootstrap | GUI légère, interface moderne et cohérente |
| **Base de données** | SQLite | Fiabilité, simplicité, pas de serveur requis |
| **Export PDF** | ReportLab | Génération de relevés et attestations |
| **Export Excel** | openpyxl | Export de données académiques |

### Architecture

L'architecture de l'application est organisée autour de trois éléments principaux :

- **Interface utilisateur** : Responsable de l'affichage et des interactions
- **Logique applicative** : Gère les traitements et les règles métier
- **Base de données** : Assure le stockage et la persistance des données

Cette organisation permet une séparation claire des responsabilités et facilite la maintenance ainsi que l'évolution future de l'application.

---

## Conception de la base de données

La base de données constitue le cœur de l'application, car elle assure la centralisation, la cohérence et la persistance de l'ensemble des informations académiques. Une base de données relationnelle SQLite a été mise en place afin de stocker de manière structurée les données relatives aux étudiants, aux structures académiques et au suivi pédagogique.

### Tables principales

| Table | Rôle |
|-------|------|
| **etudiants** | Informations personnelles et administratives des étudiants |
| **filieres** | Offre de formation |
| **niveaux** | Niveaux d'études (L1, L2, L3, M1, M2, etc.) |
| **modules** | Matières enseignées |
| **inscriptions** | Parcours académiques par année universitaire |
| **notes** | Résultats des étudiants par module |
| **notes_audit** | Traçabilité des modifications de notes |
| **absences** | Enregistrement et suivi de l'assiduité |
| **enseignants** | Informations sur les enseignants |
| **enseignements** | Affectation des enseignants aux modules |
| **semestres** | Organisation du calendrier académique |
| **periodes** | Périodes d'examens, vacances, etc. |
| **users** | Gestion d'authentification |

### Intégrité des données

L'intégrité des données est garantie par l'utilisation de :
- Clés primaires
- Clés étrangères avec cascades appropriées
- Contraintes relationnelles
- Contrôles de validité aux niveaux application et base de données

---

## Fonctionnalités principales de l'application

L'application est structurée en **10 onglets**, chacun regroupant des actions ciblées afin de gérer les données académiques stockées dans la base SQLite.

### 1. Onglet Étudiants

- Ajout d'un étudiant avec : nom, prénom, email
- Génération automatique d'un matricule unique (format ETU + lettres + compteur)
- Affichage de la liste des étudiants dans un tableau (Treeview)
- Ouverture d'une fiche étudiant au double-clic, contenant :
  - Identité (matricule, nom, prénom, email, statut)
  - Historique des inscriptions
  - Notes
  - Absences
- Import CSV d'étudiants
- Export de la liste des étudiants en CSV et Excel

<img width="951" height="500" alt="image" src="https://github.com/user-attachments/assets/c7094730-6601-4ec3-81f7-d35be22fdc8a" />
<img width="951" height="500" alt="image" src="https://github.com/user-attachments/assets/c7094730-6601-4ec3-81f7-d35be22fdc8a" />

<img width="951" height="497" alt="image" src="https://github.com/user-attachments/assets/14a47dc5-5485-4251-939d-6f8ed8c80903" />
<img width="951" height="497" alt="image" src="https://github.com/user-attachments/assets/14a47dc5-5485-4251-939d-6f8ed8c80903" />


### 2. Onglet Filières & Niveaux

- Ajout de filières (code, nom) avec contrôle d'unicité du code
- Ajout de niveaux (code, nom, ordre) avec contrôle du champ ordre (entier)
- Affichage des listes filières/niveaux
- Alimentation des listes déroulantes utilisées dans les autres onglets

<img width="855" height="448" alt="image" src="https://github.com/user-attachments/assets/eeffa33a-3482-4559-9ce8-4b7483d2d4cb" />
<img width="855" height="448" alt="image" src="https://github.com/user-attachments/assets/eeffa33a-3482-4559-9ce8-4b7483d2d4cb" />


### 3. Onglet Inscriptions

- Création d'une inscription via sélection d'étudiant, filière, niveau et année académique
- Affichage de l'historique des inscriptions dans un tableau

<img width="950" height="500" alt="image" src="https://github.com/user-attachments/assets/ace35e1e-1de4-4303-9ee9-e708cf035451" />
<img width="950" height="500" alt="image" src="https://github.com/user-attachments/assets/ace35e1e-1de4-4303-9ee9-e708cf035451" />


### 4. Onglet Modules & Notes

#### Modules
- Ajout d'un module : code, nom, coefficient, crédits, filière, niveau
- Affichage de la liste des modules
- Alimentation des listes déroulantes

#### Notes
- Ajout d'une note avec contrôle (0 à 20)
- Type d'évaluation et année académique (optionnels)
- Consultation des notes dans un tableau
- Modification et suppression des notes via sélection
- Calcul de la moyenne générale pondérée par les coefficients
- **Traçabilité complète** : table `notes_audit` enregistre INSERT/UPDATE/DELETE avec date et utilisateur

<img width="950" height="499" alt="image" src="https://github.com/user-attachments/assets/5c2ffa73-5e1a-465b-ae04-b2642f76f7f6" />
<img width="950" height="499" alt="image" src="https://github.com/user-attachments/assets/5c2ffa73-5e1a-465b-ae04-b2642f76f7f6" />


### 5. Onglet Absences

- Enregistrement d'une absence : date, justificatif (oui/non), motif
- Affichage des absences dans un tableau
- Statistiques :
  - Nombre total d'absences
  - Taux "absences par étudiant"
- Système d'alerte : liste des étudiants dépassant un seuil d'absences

<img width="945" height="631" alt="image" src="https://github.com/user-attachments/assets/4a356806-dc34-4928-9819-2f95fb691ea1" />
<img width="945" height="631" alt="image" src="https://github.com/user-attachments/assets/4a356806-dc34-4928-9819-2f95fb691ea1" />


### 6. Onglet Enseignants

- Ajout d'un enseignant : nom, prénom, email (optionnel)
- Affectation d'un enseignant à un module
- Affichage des enseignants et affectations dans deux tableaux

<img width="950" height="499" alt="image" src="https://github.com/user-attachments/assets/1a8ca908-33d3-4a4d-bdeb-85efc210786b" />
<img width="950" height="499" alt="image" src="https://github.com/user-attachments/assets/1a8ca908-33d3-4a4d-bdeb-85efc210786b" />

<img width="950" height="499" alt="image" src="https://github.com/user-attachments/assets/55d6428b-a5f4-465c-8441-e2c409e910ff" />
<img width="950" height="499" alt="image" src="https://github.com/user-attachments/assets/55d6428b-a5f4-465c-8441-e2c409e910ff" />


### 7. Onglet Calendrier

- Ajout de semestres (code, libellé, dates)
- Ajout de périodes rattachées à un semestre
- Affichage des semestres et périodes dans deux tableaux

<img width="846" height="443" alt="image" src="https://github.com/user-attachments/assets/9628f883-f355-4633-9211-ec15f0cc67c5" />
<img width="846" height="443" alt="image" src="https://github.com/user-attachments/assets/9628f883-f355-4633-9211-ec15f0cc67c5" />


### 8. Onglet Dashboard

- Indicateurs clés (KPI) :
  - Nombre d'étudiants, modules, inscriptions, absences
- Top 5 des étudiants avec le plus d'absences
- Bouton de rafraîchissement
  
<img width="950" height="499" alt="image" src="https://github.com/user-attachments/assets/48c0db8e-bd8b-4459-b5b3-8a3cacc4dcee" />
<img width="950" height="499" alt="image" src="https://github.com/user-attachments/assets/48c0db8e-bd8b-4459-b5b3-8a3cacc4dcee" />


### 9. Onglet Documents

#### Export Excel
- Notes (liste complète)
- Absences (liste complète)

<img width="852" height="448" alt="image" src="https://github.com/user-attachments/assets/bafcbd39-427c-4237-a9e6-3c43f41b8e87" />
<img width="852" height="448" alt="image" src="https://github.com/user-attachments/assets/bafcbd39-427c-4237-a9e6-3c43f41b8e87" />

#### Génération PDF
- Relevé de notes d'un étudiant avec moyenne générale pondérée
- Attestation de scolarité pour une année académique donnée

<img width="693" height="364" alt="image" src="https://github.com/user-attachments/assets/b1002c22-90f2-40c4-8129-fc0baacd80b8" />
<img width="693" height="364" alt="image" src="https://github.com/user-attachments/assets/b1002c22-90f2-40c4-8129-fc0baacd80b8" />

<img width="676" height="421" alt="image" src="https://github.com/user-attachments/assets/6938d832-9726-4db1-a10e-73849c0bba22" />
<img width="676" height="421" alt="image" src="https://github.com/user-attachments/assets/6938d832-9726-4db1-a10e-73849c0bba22" />




### 10. Onglet Gestion utilisateurs

- Ajout de nouveaux utilisateurs (username, nom, prénom, email, mot de passe, rôle)
- Modification des informations utilisateurs
- Réitialisation mot de passe
- Activation/Désactivation de l'accès d'un utilisateur

<img width="748" height="423" alt="image" src="https://github.com/user-attachments/assets/73f95348-5a6b-4349-92ab-1a90c6b0cd98" />
<img width="748" height="423" alt="image" src="https://github.com/user-attachments/assets/73f95348-5a6b-4349-92ab-1a90c6b0cd98" />

---

## Installation et utilisation

### Prérequis

- Python 3.7+
- pip (gestionnaire de paquets Python)

### Installation des dépendances

```bash
pip install ttkbootstrap reportlab openpyxl
```

### Lancer l'application

```bash
python gestion_etudiants/main.py
```

### Identifiants par défaut

| Champ | Valeur |
|-------|--------|
| **Utilisateur** | `admin` |
| **Mot de passe** | `admin123` |

---

## Synthèse

L'application développée permet de couvrir l'ensemble des fonctionnalités essentielles décrites dans le cahier des charges. Les différents modules sont opérationnels et interconnectés autour d'une base de données SQLite centralisée.

- **Gestion des étudiants** : Ajout manuel, import CSV, consultation détaillée
- **Structures académiques** : Configuration simple et fiable des filières, niveaux, modules
- **Gestion des notes** : Saisie, modification, traçabilité complète, calculs automatiques
- **Suivi des absences** : Enregistrement, alertes, statistiques
- **Tableau de bord** : Indicateurs clés et classements
- **Documents officiels** : Relevés PDF, attestations, exports Excel

---

## Limites et perspectives d'amélioration

### Limites actuelles

- **Architecture monolithique** : Interface, logique métier et BD dans le même projet
- **Interface Tkinter** : Fonctionnelle mais limitée en personnalisation
- **Pas de tests automatisés** : Risque de régressions lors des évolutions
- **Usage local mono-utilisateur** : Pas de gestion de concurrence ni accès distant

### Perspectives d'amélioration

1. **Architecture modulaire** : Faciliter la maintenance et l'évolution
2. **Version web** : API REST + interface web pour accès multi-utilisateurs et distant
3. **Graphiques avancés** : Statistiques visualisées (matplotlib, plotly)
4. **Gestion des rôles détaillée** : Permissions granulaires par profil utilisateur
5. **Tests automatisés** : Suite de tests complète (unittest, pytest)
6. **Informations étudiants enrichies** : Date/lieu de naissance, photo, sexe, adresse, téléphone
7. **Gestion des groupes** : Affectation par groupe d'étude
8. **Spécialités** : Gestion des spécialités au sein des filières
9. **Classements et mentions** : Calcul automatique des mentions académiques

---

## Conclusion

Ce projet a permis de concevoir et de développer une application desktop complète de gestion des étudiants, couvrant l'ensemble du cycle académique, de l'inscription au suivi des résultats et de l'assiduité. L'application centralise les données académiques dans une base de données SQLite cohérente et sécurisée, et propose des fonctionnalités adaptées aux besoins administratifs et pédagogiques.

Au-delà de l'aspect fonctionnel, ce projet a permis de mettre en pratique des compétences essentielles en :
- **Programmation Python** : Développement de logiciels structurés
- **Conception de bases de données** : Modèle relationnel, intégrité des données
- **Développement d'interfaces graphiques** : Tkinter, UX/UI
- **Architecture logicielle** : Séparation des responsabilités, maintenabilité

Il constitue une synthèse concrète des connaissances acquises au cours de la formation et une base solide pour des évolutions futures.

---

## Technologies utilisées

```python
# Core
python 3.x

# GUI
tkinter
ttkbootstrap

# Database
sqlite3

# Export
reportlab  # PDF
openpyxl   # Excel

# Utilities
hashlib    # Sécurité (hashage passwords)
csv        # Import/Export
datetime   # Gestion des dates
pathlib    # Gestion des chemins
```

---

## Structure du projet

```
gestion_etudiants/
├── main.py                    # Application principale
├── db/
│   └── database.db            # Base de données SQLite
└── README.md                  # Documentation
```

---

## Auteurs

- **Yobe GNADAME**
- **Mileina Malou**
- **Jean-Eudes Wandji**

---

## Licence

Projet académique - ESILV MACSIN4A0425 (2026)
