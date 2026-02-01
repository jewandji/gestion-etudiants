#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'importation des modules pour MSc1 CSDS (Msc1 Computer Science & Data Science)
"""

import sqlite3
import os
import sys

# Ajouter le chemin pour importer depuis main.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'gestion_etudiants'))

DB_PATH = os.path.join(os.path.dirname(__file__), 'db', 'database.db')

def db_connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_tables_exist():
    """Ensure all database tables are created"""
    conn = db_connect()
    cur = conn.cursor()
    
    try:
        # Create all necessary tables
        cur.execute("""
            CREATE TABLE IF NOT EXISTS filieres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                nom TEXT NOT NULL
            );
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS niveaux (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                nom TEXT NOT NULL,
                ordre INTEGER
            );
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS modules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                nom TEXT NOT NULL,
                coefficient REAL NOT NULL,
                credits INTEGER,
                filiere_id INTEGER,
                niveau_id INTEGER,
                FOREIGN KEY(filiere_id) REFERENCES filieres(id) ON DELETE SET NULL,
                FOREIGN KEY(niveau_id) REFERENCES niveaux(id) ON DELETE SET NULL
            );
        """)
        
        conn.commit()
        print("✓ Tables de base créées/vérifiées")
    except Exception as e:
        print(f"Erreur lors de la création des tables: {e}")
        conn.rollback()
    finally:
        conn.close()

# Données des modules MSc1 CSDS - 1ère année
MODULES_YEAR1 = [
    # UE: Programming
    {"code": "MSC1-PROG-PY", "nom": "Python for Data Science", "coefficient": 1.0, "credits": 3, "semestre": "S07", "unite": "Programming"},
    {"code": "MSC1-PROG-OOP", "nom": "Object Oriented Programming Lab", "coefficient": 1.0, "credits": 3, "semestre": "S07", "unite": "Programming"},
    
    # UE: Cloud computing
    {"code": "MSC1-CLOUD-CC", "nom": "Cloud computing", "coefficient": 1.0, "credits": 3, "semestre": "S08", "unite": "Cloud computing"},
    {"code": "MSC1-CLOUD-AN", "nom": "Advanced Network", "coefficient": 1.0, "credits": 3, "semestre": "S08", "unite": "Cloud computing"},
    
    # UE: Database Engineering
    {"code": "MSC1-DB-ADV", "nom": "Advanced database management", "coefficient": 1.0, "credits": 3, "semestre": "S07", "unite": "Database Engineering"},
    {"code": "MSC1-DB-NOSQL", "nom": "Advanced topics in NoSql databases", "coefficient": 1.0, "credits": 4, "semestre": "S08", "unite": "Database Engineering"},
    
    # UE: Data Lab
    {"code": "MSC1-DL-ML", "nom": "Machine Learning and clustering", "coefficient": 1.0, "credits": 4, "semestre": "S08", "unite": "Data Lab"},
    {"code": "MSC1-DL-LAB", "nom": "Data Lab", "coefficient": 1.0, "credits": 3, "semestre": "S08", "unite": "Data Lab"},
    
    # UE: Advanced Programming
    {"code": "MSC1-AP-DP", "nom": "Design pattern & software engineering", "coefficient": 1.0, "credits": 3, "semestre": "S07", "unite": "Advanced Programming"},
    {"code": "MSC1-AP-ALGO", "nom": "Advanced Data Structures & Algorithms", "coefficient": 1.0, "credits": 3, "semestre": "S07", "unite": "Advanced Programming"},
    {"code": "MSC1-AP-WEB", "nom": "Web Application Architectures", "coefficient": 1.0, "credits": 3, "semestre": "S08", "unite": "Advanced Programming"},
    {"code": "MSC1-AP-3D", "nom": "3D programming", "coefficient": 1.0, "credits": 3, "semestre": "S08", "unite": "Advanced Programming"},
    
    # UE: Soft Skills
    {"code": "MSC1-SS-GR1", "nom": "Getting ready 1", "coefficient": 0.0, "credits": 0, "semestre": "S07", "unite": "Soft Skills"},
    {"code": "MSC1-SS-COM", "nom": "Communication in English", "coefficient": 1.0, "credits": 2, "semestre": "S07-S08", "unite": "Soft Skills"},
    
    # UE: Rapport d'alternance
    {"code": "MSC1-RA-INT", "nom": "Rapport d'alternance - Période intermédiaire", "coefficient": 1.0, "credits": 10, "semestre": "S07", "unite": "Rapport d'alternance"},
    {"code": "MSC1-RA-ANN", "nom": "Rapport d'alternance - Période annuelle", "coefficient": 1.0, "credits": 10, "semestre": "S08", "unite": "Rapport d'alternance"},
]

# Données des modules MSc1 CSDS - 2ème année
MODULES_YEAR2 = [
    # UE: Advanced programming
    {"code": "MSC1-AP2-BIG", "nom": "Big data processing in Spark", "coefficient": 1.0, "credits": 4, "semestre": "S09", "unite": "Advanced programming"},
    {"code": "MSC1-AP2-WS", "nom": "Web scraping & Data Processing", "coefficient": 1.0, "credits": 4, "semestre": "S09", "unite": "Advanced programming"},
    
    # UE: Immersives technologies
    {"code": "MSC1-IMM-TECH", "nom": "Immersives technologies", "coefficient": 1.0, "credits": 2, "semestre": "S09", "unite": "Immersives technologies"},
    
    # UE: Database engineering
    {"code": "MSC1-DB2-GREEN", "nom": "Green AI & Ethics", "coefficient": 1.0, "credits": 2, "semestre": "S09", "unite": "Database engineering"},
    {"code": "MSC1-DB2-GRAPH", "nom": "Graph and mining", "coefficient": 1.0, "credits": 2, "semestre": "S09", "unite": "Database engineering"},
    
    # UE: Data Toolkits
    {"code": "MSC1-DT-VIZ", "nom": "Data visualization", "coefficient": 1.0, "credits": 2, "semestre": "S09", "unite": "Data Toolkits"},
    {"code": "MSC1-DT-NLP", "nom": "Natural Language Processing", "coefficient": 1.0, "credits": 2, "semestre": "S09", "unite": "Data Toolkits"},
    {"code": "MSC1-DT-BI", "nom": "Business Intelligence", "coefficient": 1.0, "credits": 2, "semestre": "S09", "unite": "Data Toolkits"},
    
    # UE: Machine Learning Use-cases
    {"code": "MSC1-ML-CV", "nom": "Computer Vision", "coefficient": 1.0, "credits": 2, "semestre": "S09", "unite": "Machine Learning Use-cases"},
    {"code": "MSC1-ML-UC", "nom": "Machine Learning Use-cases", "coefficient": 1.0, "credits": 4, "semestre": "S09", "unite": "Machine Learning Use-cases"},
    
    # UE: Machine Learning Operations
    {"code": "MSC1-MLO-OPS", "nom": "Machine Learning Operations", "coefficient": 1.0, "credits": 2, "semestre": "S09", "unite": "Machine Learning Operations"},
    
    # UE: Security
    {"code": "MSC1-SEC-THEORY", "nom": "Theory and Practice of Security and Privacy", "coefficient": 1.0, "credits": 4, "semestre": "S10", "unite": "Security"},
    {"code": "MSC1-SEC-SOFT", "nom": "Secure software developpement", "coefficient": 1.0, "credits": 4, "semestre": "S10", "unite": "Security"},
    
    # UE: Softskills
    {"code": "MSC1-SS2-WORK", "nom": "Communication for the workplace", "coefficient": 1.0, "credits": 2, "semestre": "S09-S10", "unite": "Softskills"},
    {"code": "MSC1-SS2-GR2", "nom": "Getting ready 2", "coefficient": 0.0, "credits": 0, "semestre": "S09", "unite": "Softskills"},
    {"code": "MSC1-SS2-BOOT", "nom": "Thesis Bootcamp", "coefficient": 1.0, "credits": 2, "semestre": "S10", "unite": "Softskills"},
    {"code": "MSC1-SS2-CAREER", "nom": "Career Development", "coefficient": 0.0, "credits": 0, "semestre": "S09", "unite": "Softskills"},
    {"code": "MSC1-SS2-MBTI", "nom": "MBTI", "coefficient": 0.0, "credits": 0, "semestre": "S09", "unite": "Softskills"},
    
    # UE: Rapport d'alternance (2ème année)
    {"code": "MSC1-RA2-INT", "nom": "Rapport d'alternance - Période intermédiaire", "coefficient": 1.0, "credits": 10, "semestre": "S07", "unite": "Rapport d'alternance"},
    {"code": "MSC1-RA2-ANN", "nom": "Rapport d'alternance - Période annuelle", "coefficient": 1.0, "credits": 10, "semestre": "S08", "unite": "Rapport d'alternance"},
]

def import_modules():
    """Import all MSc1 CSDS modules into the database"""
    
    # D'abord, assurer que les tables existent
    ensure_tables_exist()
    
    conn = db_connect()
    cur = conn.cursor()
    
    try:
        # Vérifier ou créer la filière MSc1 CSDS
        cur.execute("SELECT id FROM filieres WHERE code = ?", ("MSC1-CSDS",))
        filiere = cur.fetchone()
        
        if not filiere:
            print("✓ Création de la filière MSc1 CSDS...")
            cur.execute(
                "INSERT INTO filieres (code, nom) VALUES (?, ?)",
                ("MSC1-CSDS", "Master of Science 1 - Computer Science & Data Science")
            )
            conn.commit()
            cur.execute("SELECT id FROM filieres WHERE code = ?", ("MSC1-CSDS",))
            filiere = cur.fetchone()
            filiere_id = filiere['id']
        else:
            filiere_id = filiere['id']
            print(f"✓ Filière MSc1 CSDS trouvée (ID: {filiere_id})")
        
        # Vérifier ou créer les niveaux S07, S08, S09, S10
        semestres = {
            "S07": "Semestre 7 (1ère année - Automne)",
            "S08": "Semestre 8 (1ère année - Printemps)",
            "S09": "Semestre 9 (2ème année - Automne)",
            "S10": "Semestre 10 (2ère année - Printemps)"
        }
        
        niveau_ids = {}
        for code, nom in semestres.items():
            cur.execute("SELECT id FROM niveaux WHERE code = ?", (code,))
            niveau = cur.fetchone()
            if not niveau:
                ordre = int(code[1:])
                cur.execute(
                    "INSERT INTO niveaux (code, nom, ordre) VALUES (?, ?, ?)",
                    (code, nom, ordre)
                )
                conn.commit()
                cur.execute("SELECT id FROM niveaux WHERE code = ?", (code,))
                niveau = cur.fetchone()
            niveau_ids[code] = niveau['id']
            print(f"✓ Niveau {code} trouvé/créé (ID: {niveau['id']})")
        
        # Insérer les modules de la 1ère année
        print("\n--- Importation des modules 1ère année ---")
        count = 0
        for module_data in MODULES_YEAR1:
            code = module_data["code"]
            nom = module_data["nom"]
            coefficient = module_data["coefficient"]
            credits = module_data["credits"]
            semestre = module_data["semestre"]
            
            # Obtenir le niveau_id basé sur le semestre
            semestres_list = semestre.split("-") if "-" in semestre else [semestre]
            niveau_id = niveau_ids.get(semestres_list[0])
            
            try:
                cur.execute(
                    "INSERT INTO modules (code, nom, coefficient, credits, filiere_id, niveau_id) VALUES (?, ?, ?, ?, ?, ?)",
                    (code, nom, coefficient, credits, filiere_id, niveau_id)
                )
                print(f"  ✓ {code}: {nom} (Crédit: {credits}, Semestre: {semestre})")
                count += 1
            except sqlite3.IntegrityError:
                print(f"  ⚠ {code} existe déjà")
        
        conn.commit()
        print(f"\n✓ {count} modules de 1ère année importés")
        
        # Insérer les modules de la 2ère année
        print("\n--- Importation des modules 2ère année ---")
        count = 0
        for module_data in MODULES_YEAR2:
            code = module_data["code"]
            nom = module_data["nom"]
            coefficient = module_data["coefficient"]
            credits = module_data["credits"]
            semestre = module_data["semestre"]
            
            # Obtenir le niveau_id basé sur le semestre
            semestres_list = semestre.split("-") if "-" in semestre else [semestre]
            niveau_id = niveau_ids.get(semestres_list[0])
            
            try:
                cur.execute(
                    "INSERT INTO modules (code, nom, coefficient, credits, filiere_id, niveau_id) VALUES (?, ?, ?, ?, ?, ?)",
                    (code, nom, coefficient, credits, filiere_id, niveau_id)
                )
                print(f"  ✓ {code}: {nom} (Crédit: {credits}, Semestre: {semestre})")
                count += 1
            except sqlite3.IntegrityError:
                print(f"  ⚠ {code} existe déjà")
        
        conn.commit()
        print(f"\n✓ {count} modules de 2ère année importés")
        
        # Afficher le résumé
        cur.execute(
            "SELECT COUNT(*) as count FROM modules WHERE filiere_id = ?",
            (filiere_id,)
        )
        total = cur.fetchone()['count']
        print(f"\n✅ Total: {total} modules pour MSc1 CSDS")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'importation: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Importation des modules MSc1 CSDS")
    print("=" * 60)
    import_modules()
