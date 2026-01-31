from pathlib import Path
import sqlite3
import hashlib
import csv
from datetime import datetime

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import ttkbootstrap as ttkb

# PDF / Excel
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from openpyxl import Workbook


# PATHS

BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "db"
DB_PATH = DB_DIR / "database.db"


# DB HELPERS

def db_connect():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def now_iso():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def ensure_tables_and_seed():
    conn = db_connect()
    cur = conn.cursor()

    # core
    cur.execute("""
        CREATE TABLE IF NOT EXISTS etudiants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matricule TEXT UNIQUE NOT NULL,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            email TEXT UNIQUE,
            statut TEXT DEFAULT 'actif'
        );
    """)

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
        CREATE TABLE IF NOT EXISTS inscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            etudiant_id INTEGER NOT NULL,
            filiere_id INTEGER NOT NULL,
            niveau_id INTEGER NOT NULL,
            annee_academique TEXT NOT NULL,
            statut TEXT DEFAULT 'inscrit',
            FOREIGN KEY(etudiant_id) REFERENCES etudiants(id) ON DELETE CASCADE,
            FOREIGN KEY(filiere_id) REFERENCES filieres(id) ON DELETE RESTRICT,
            FOREIGN KEY(niveau_id) REFERENCES niveaux(id) ON DELETE RESTRICT
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

    cur.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            etudiant_id INTEGER NOT NULL,
            module_id INTEGER NOT NULL,
            note REAL NOT NULL,
            type_evaluation TEXT,
            annee_academique TEXT,
            FOREIGN KEY(etudiant_id) REFERENCES etudiants(id) ON DELETE CASCADE,
            FOREIGN KEY(module_id) REFERENCES modules(id) ON DELETE CASCADE
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS notes_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            old_value TEXT,
            new_value TEXT,
            changed_at TEXT NOT NULL,
            changed_by TEXT NOT NULL,
            FOREIGN KEY(note_id) REFERENCES notes(id) ON DELETE CASCADE
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS absences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            etudiant_id INTEGER NOT NULL,
            module_id INTEGER NOT NULL,
            date_absence TEXT NOT NULL,
            justifiee INTEGER DEFAULT 0,
            motif TEXT,
            FOREIGN KEY(etudiant_id) REFERENCES etudiants(id) ON DELETE CASCADE,
            FOREIGN KEY(module_id) REFERENCES modules(id) ON DELETE CASCADE
        );
    """)

    # teachers 
    cur.execute("""
        CREATE TABLE IF NOT EXISTS enseignants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            email TEXT UNIQUE
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS enseignements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            enseignant_id INTEGER NOT NULL,
            module_id INTEGER NOT NULL,
            annee_academique TEXT,
            UNIQUE(enseignant_id, module_id, annee_academique),
            FOREIGN KEY(enseignant_id) REFERENCES enseignants(id) ON DELETE CASCADE,
            FOREIGN KEY(module_id) REFERENCES modules(id) ON DELETE CASCADE
        );
    """)

    # academic calendar
    cur.execute("""
        CREATE TABLE IF NOT EXISTS semestres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            libelle TEXT,
            date_debut TEXT NOT NULL,
            date_fin TEXT NOT NULL
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS periodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            semestre_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            libelle TEXT,
            date_debut TEXT NOT NULL,
            date_fin TEXT NOT NULL,
            FOREIGN KEY(semestre_id) REFERENCES semestres(id) ON DELETE CASCADE
        );
    """)

    # login/users 
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            actif INTEGER DEFAULT 1
        );
    """)

    # seed admin if none
    cur.execute("SELECT COUNT(*) FROM users;")
    if cur.fetchone()[0] == 0:
        cur.execute("""
            INSERT INTO users (username, password_hash, role, actif)
            VALUES (?, ?, ?, 1);
        """, ("admin", hash_password("admin123"), "ADMIN"))

    conn.commit()
    conn.close()


# EXPORT HELPERS

def export_query_to_xlsx(headers, rows, filepath: str, sheet_name="Export"):
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name[:31]
    ws.append(headers)
    for r in rows:
        ws.append(list(r))
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    wb.save(filepath)


def _pdf_header(c, title: str):
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, 28.5 * cm, title)
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, 28.0 * cm, f"Généré le {datetime.now().strftime('%Y-%m-%d %H:%M')}")


def generate_transcript_pdf(conn, etudiant_id: int, filepath: str):
    cur = conn.cursor()
    cur.execute("SELECT matricule, nom, prenom, COALESCE(email,'') FROM etudiants WHERE id=?", (etudiant_id,))
    etu = cur.fetchone()
    if not etu:
        raise ValueError("Étudiant introuvable")

    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(filepath, pagesize=A4)
    _pdf_header(c, "Relevé de notes")

    matricule, nom, prenom, email = etu
    c.setFont("Helvetica", 11)
    c.drawString(2 * cm, 26.8 * cm, f"Étudiant : {nom} {prenom}")
    c.drawString(2 * cm, 26.2 * cm, f"Matricule : {matricule}")
    if email:
        c.drawString(2 * cm, 25.6 * cm, f"Email : {email}")

    cur.execute("""
        SELECT m.code, m.nom, m.coefficient, no.note, COALESCE(no.annee_academique,''), COALESCE(no.type_evaluation,'')
        FROM notes no
        JOIN modules m ON m.id = no.module_id
        WHERE no.etudiant_id=?
        ORDER BY COALESCE(no.annee_academique,''), m.code
    """, (etudiant_id,))
    rows = cur.fetchall()

    y = 24.5 * cm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2 * cm, y, "Module")
    c.drawString(10 * cm, y, "Coef")
    c.drawString(12 * cm, y, "Note")
    c.drawString(14 * cm, y, "Année")
    y -= 0.6 * cm

    c.setFont("Helvetica", 10)
    total_points = 0.0
    total_coef = 0.0

    for code, mnom, coef, note, annee, typ in rows:
        if y < 2.5 * cm:
            c.showPage()
            _pdf_header(c, "Relevé de notes (suite)")
            y = 26.5 * cm
            c.setFont("Helvetica", 10)

        c.drawString(2 * cm, y, f"{code} - {mnom}"[:60])
        c.drawString(10 * cm, y, f"{coef}")
        c.drawString(12 * cm, y, f"{note}")
        c.drawString(14 * cm, y, annee)
        y -= 0.5 * cm

        try:
            total_points += float(note) * float(coef)
            total_coef += float(coef)
        except Exception:
            pass

    y -= 0.4 * cm
    c.setFont("Helvetica-Bold", 11)
    if total_coef > 0:
        moyenne = total_points / total_coef
        c.drawString(2 * cm, y, f"Moyenne générale : {moyenne:.2f} / 20")
    else:
        c.drawString(2 * cm, y, "Moyenne générale : -")

    c.save()


def generate_attestation_pdf(conn, etudiant_id: int, annee: str, filepath: str):
    cur = conn.cursor()
    cur.execute("SELECT matricule, nom, prenom FROM etudiants WHERE id=?", (etudiant_id,))
    etu = cur.fetchone()
    if not etu:
        raise ValueError("Étudiant introuvable")

    cur.execute("""
        SELECT f.code, f.nom, n.code, n.nom, COALESCE(i.statut,'')
        FROM inscriptions i
        JOIN filieres f ON f.id=i.filiere_id
        JOIN niveaux n ON n.id=i.niveau_id
        WHERE i.etudiant_id=? AND i.annee_academique=?
        ORDER BY i.id DESC
        LIMIT 1
    """, (etudiant_id, annee))
    ins = cur.fetchone()
    if not ins:
        raise ValueError("Aucune inscription pour cette année")

    matricule, nom, prenom = etu
    fcode, fnom, ncode, nnom, statut = ins

    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(filepath, pagesize=A4)
    _pdf_header(c, "Attestation de scolarité")

    c.setFont("Helvetica", 12)
    text = c.beginText(2 * cm, 25.5 * cm)
    text.textLine("Je soussigné(e), certifie que :")
    text.textLine("")
    text.textLine(f"{nom} {prenom} (matricule : {matricule})")
    text.textLine("")
    text.textLine(f"est inscrit(e) pour l'année académique : {annee}")
    text.textLine(f"Filière : {fcode} - {fnom}")
    text.textLine(f"Niveau : {ncode} - {nnom}")
    text.textLine(f"Statut : {statut}")
    text.textLine("")
    text.textLine("Fait pour servir et valoir ce que de droit.")
    c.drawText(text)

    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, 4 * cm, "Signature : ____________________________")

    c.save()


# MAIN APP

class App(tk.Toplevel):
    def __init__(self, parent, username: str, root=None):
        super().__init__(parent)
        self.username = username
        self.root = root

        self.title("Gestion des étudiants")
        self.geometry("1100x700")
        self.resizable(False, False)
        
        # Fermer l'application complètement quand on ferme cette fenêtre
        self.protocol("WM_DELETE_WINDOW", self.close_app)

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_etudiants = ttk.Frame(self.tabs)
        self.tab_academique = ttk.Frame(self.tabs)
        self.tab_inscriptions = ttk.Frame(self.tabs)
        self.tab_notes = ttk.Frame(self.tabs)
        self.tab_absences = ttk.Frame(self.tabs)
        self.tab_enseignants = ttk.Frame(self.tabs)
        self.tab_calendrier = ttk.Frame(self.tabs)
        self.tab_dashboard = ttk.Frame(self.tabs)
        self.tab_documents = ttk.Frame(self.tabs)

        self.tabs.add(self.tab_etudiants, text="Étudiants")
        self.tabs.add(self.tab_academique, text="Filières & Niveaux")
        self.tabs.add(self.tab_inscriptions, text="Inscriptions")
        self.tabs.add(self.tab_notes, text="Modules & Notes")
        self.tabs.add(self.tab_absences, text="Absences")
        self.tabs.add(self.tab_enseignants, text="Enseignants")
        self.tabs.add(self.tab_calendrier, text="Calendrier")
        self.tabs.add(self.tab_dashboard, text="Dashboard")
        self.tabs.add(self.tab_documents, text="Documents")

        self.build_etudiants_tab()
        self.build_academique_tab()
        self.build_inscriptions_tab()
        self.build_notes_tab()
        self.build_absences_tab()
        self.build_enseignants_tab()
        self.build_calendrier_tab()
        self.build_dashboard_tab()
        self.build_documents_tab()

        self.refresh_all()

    # UTIL

    def parse_id_from_combo(self, s: str):
        if not s:
            return None
        part = s.split("-", 1)[0].strip()
        return int(part) if part.isdigit() else None

    def refresh_all(self):
        self.refresh_etudiants_list()
        self.refresh_filieres()
        self.refresh_niveaux()
        self.refresh_inscriptions_lists()
        self.refresh_modules_list()
        self.refresh_notes_lists()
        self.refresh_absences()
        self.refresh_enseignants()
        self.refresh_calendrier()
        self.refresh_dashboard()
        self.refresh_documents_lists()

    # ETUDIANTS

    def build_etudiants_tab(self):
        frm = ttk.Frame(self.tab_etudiants, padding=10)
        frm.pack(fill="both", expand=True)

        left = ttk.LabelFrame(frm, text="Ajouter un étudiant", padding=10)
        left.pack(side="left", fill="y", padx=(0, 10))

        ttk.Label(left, text="Nom").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Label(left, text="Prénom").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Label(left, text="Email").grid(row=2, column=0, sticky="w", pady=4)

        self.e_nom = ttk.Entry(left, width=28)
        self.e_prenom = ttk.Entry(left, width=28)
        self.e_email = ttk.Entry(left, width=28)

        self.e_nom.grid(row=0, column=1, pady=4)
        self.e_prenom.grid(row=1, column=1, pady=4)
        self.e_email.grid(row=2, column=1, pady=4)

        ttk.Button(left, text="Ajouter", command=self.add_etudiant).grid(row=3, column=1, sticky="e", pady=(10, 0))

        ttk.Separator(left, orient="horizontal").grid(row=4, column=0, columnspan=2, sticky="ew", pady=12)

        ttk.Button(left, text="Importer CSV", command=self.import_etudiants_csv).grid(row=5, column=0, columnspan=2, sticky="ew", pady=4)
        ttk.Button(left, text="Exporter CSV", command=self.export_etudiants_csv).grid(row=6, column=0, columnspan=2, sticky="ew", pady=4)
        ttk.Button(left, text="Exporter Excel", command=self.export_etudiants_xlsx).grid(row=7, column=0, columnspan=2, sticky="ew", pady=4)

        right = ttk.LabelFrame(frm, text="Liste des étudiants (double-clic = fiche)", padding=10)
        right.pack(side="left", fill="both", expand=True)

        cols = ("id", "matricule", "nom", "prenom", "email", "statut")
        self.tree_etudiants = ttk.Treeview(right, columns=cols, show="headings", height=22)
        for c in cols:
            self.tree_etudiants.heading(c, text=c)
            self.tree_etudiants.column(c, width=120 if c != "email" else 260, anchor="w")
        self.tree_etudiants.column("id", width=50, anchor="center")

        self.tree_etudiants.pack(fill="both", expand=True)
        self.tree_etudiants.bind("<Double-1>", self.open_fiche_etudiant)

    def generate_matricule(self, nom: str, prenom: str) -> str:
        base = f"ETU{nom[:2].upper()}{prenom[:2].upper()}"
        conn = db_connect()
        cur = conn.cursor()
        i = 1
        matricule = base
        while True:
            cur.execute("SELECT 1 FROM etudiants WHERE matricule = ?", (matricule,))
            if cur.fetchone() is None:
                break
            i += 1
            matricule = f"{base}{i}"
        conn.close()
        return matricule

    def add_etudiant(self):
        nom = self.e_nom.get().strip()
        prenom = self.e_prenom.get().strip()
        email = self.e_email.get().strip()

        if not nom or not prenom:
            messagebox.showerror("Erreur", "Nom et prénom obligatoires.")
            return

        matricule = self.generate_matricule(nom, prenom)

        conn = db_connect()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO etudiants (matricule, nom, prenom, email, statut) VALUES (?, ?, ?, ?, ?)",
                (matricule, nom, prenom, email if email else None, "actif"),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erreur", "Email déjà utilisé (ou conflit matricule).")
        finally:
            conn.close()

        self.e_nom.delete(0, tk.END)
        self.e_prenom.delete(0, tk.END)
        self.e_email.delete(0, tk.END)

        self.refresh_all()
        messagebox.showinfo("OK", f"Étudiant ajouté ({matricule}).")

    def refresh_etudiants_list(self):
        if not hasattr(self, "tree_etudiants"):
            return
        for row in self.tree_etudiants.get_children():
            self.tree_etudiants.delete(row)

        conn = db_connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, matricule, nom, prenom, COALESCE(email,''), COALESCE(statut,'')
            FROM etudiants
            ORDER BY id DESC
        """)
        rows = cur.fetchall()
        conn.close()

        for r in rows:
            self.tree_etudiants.insert("", "end", values=r)

    def open_fiche_etudiant(self, event=None):
        sel = self.tree_etudiants.selection()
        if not sel:
            return
        values = self.tree_etudiants.item(sel[0], "values")
        etu_id = int(values[0])

        w = tk.Toplevel(self)
        w.title("Fiche étudiant")
        w.geometry("900x520")
        w.resizable(False, False)

        frm = ttk.Frame(w, padding=10)
        frm.pack(fill="both", expand=True)

        box_id = ttk.LabelFrame(frm, text="Identité", padding=10)
        box_id.pack(fill="x")

        conn = db_connect()
        cur = conn.cursor()
        cur.execute("SELECT matricule, nom, prenom, COALESCE(email,''), COALESCE(statut,'') FROM etudiants WHERE id=?", (etu_id,))
        etu = cur.fetchone()

        ttk.Label(box_id, text=f"Matricule : {etu[0]}").grid(row=0, column=0, sticky="w", padx=6, pady=2)
        ttk.Label(box_id, text=f"Nom : {etu[1]}").grid(row=0, column=1, sticky="w", padx=6, pady=2)
        ttk.Label(box_id, text=f"Prénom : {etu[2]}").grid(row=0, column=2, sticky="w", padx=6, pady=2)
        ttk.Label(box_id, text=f"Email : {etu[3]}").grid(row=1, column=0, sticky="w", padx=6, pady=2)
        ttk.Label(box_id, text=f"Statut : {etu[4]}").grid(row=1, column=1, sticky="w", padx=6, pady=2)

        nb = ttk.Notebook(frm)
        nb.pack(fill="both", expand=True, pady=10)

        t_ins = ttk.Frame(nb)
        t_notes = ttk.Frame(nb)
        t_abs = ttk.Frame(nb)
        nb.add(t_ins, text="Inscriptions")
        nb.add(t_notes, text="Notes")
        nb.add(t_abs, text="Absences")

        tree_i = ttk.Treeview(t_ins, columns=("annee", "filiere", "niveau", "statut"), show="headings", height=14)
        for c in ("annee", "filiere", "niveau", "statut"):
            tree_i.heading(c, text=c)
            tree_i.column(c, width=200, anchor="w")
        tree_i.pack(fill="both", expand=True, padx=10, pady=10)

        tree_n = ttk.Treeview(t_notes, columns=("annee", "module", "note", "coef", "type"), show="headings", height=14)
        for c in ("annee", "module", "note", "coef", "type"):
            tree_n.heading(c, text=c)
            tree_n.column(c, width=200, anchor="w")
        tree_n.column("note", width=80, anchor="center")
        tree_n.column("coef", width=80, anchor="center")
        tree_n.pack(fill="both", expand=True, padx=10, pady=10)

        tree_a = ttk.Treeview(t_abs, columns=("date", "module", "justifiee", "motif"), show="headings", height=14)
        for c in ("date", "module", "justifiee", "motif"):
            tree_a.heading(c, text=c)
            tree_a.column(c, width=220, anchor="w")
        tree_a.pack(fill="both", expand=True, padx=10, pady=10)

        cur.execute("""
            SELECT i.annee_academique,
                   f.code || ' - ' || f.nom,
                   n.code || ' - ' || n.nom,
                   COALESCE(i.statut,'')
            FROM inscriptions i
            JOIN filieres f ON f.id=i.filiere_id
            JOIN niveaux n ON n.id=i.niveau_id
            WHERE i.etudiant_id=?
            ORDER BY i.id DESC
        """, (etu_id,))
        for r in cur.fetchall():
            tree_i.insert("", "end", values=r)

        cur.execute("""
            SELECT COALESCE(no.annee_academique,''),
                   m.code || ' - ' || m.nom,
                   no.note,
                   m.coefficient,
                   COALESCE(no.type_evaluation,'')
            FROM notes no
            JOIN modules m ON m.id=no.module_id
            WHERE no.etudiant_id=?
            ORDER BY no.id DESC
        """, (etu_id,))
        for r in cur.fetchall():
            tree_n.insert("", "end", values=r)

        cur.execute("""
            SELECT a.date_absence,
                   m.code || ' - ' || m.nom,
                   CASE a.justifiee WHEN 1 THEN 'Oui' ELSE 'Non' END,
                   COALESCE(a.motif,'')
            FROM absences a
            JOIN modules m ON m.id=a.module_id
            WHERE a.etudiant_id=?
            ORDER BY a.date_absence DESC
        """, (etu_id,))
        for r in cur.fetchall():
            tree_a.insert("", "end", values=r)

        conn.close()

    def import_etudiants_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if not path:
            return

        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        ok = 0
        for row in rows:
            nom = (row.get("nom") or row.get("Nom") or "").strip()
            prenom = (row.get("prenom") or row.get("Prenom") or row.get("Prénom") or "").strip()
            email = (row.get("email") or row.get("Email") or "").strip()
            if not nom or not prenom:
                continue

            matricule = self.generate_matricule(nom, prenom)

            conn = db_connect()
            cur = conn.cursor()
            try:
                cur.execute(
                    "INSERT INTO etudiants (matricule, nom, prenom, email, statut) VALUES (?, ?, ?, ?, ?)",
                    (matricule, nom, prenom, email if email else None, "actif"),
                )
                conn.commit()
                ok += 1
            except sqlite3.IntegrityError:
                pass
            finally:
                conn.close()

        self.refresh_all()
        messagebox.showinfo("OK", f"Import terminé : {ok} étudiant(s).")

    def export_etudiants_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not path:
            return

        conn = db_connect()
        cur = conn.cursor()
        cur.execute("SELECT id, matricule, nom, prenom, COALESCE(email,''), COALESCE(statut,'') FROM etudiants ORDER BY id")
        rows = cur.fetchall()
        conn.close()

        with open(path, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["id", "matricule", "nom", "prenom", "email", "statut"])
            w.writerows(rows)

        messagebox.showinfo("OK", "Export CSV terminé.")

    def export_etudiants_xlsx(self):
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if not path:
            return
        conn = db_connect()
        cur = conn.cursor()
        cur.execute("SELECT id, matricule, nom, prenom, COALESCE(email,''), COALESCE(statut,'') FROM etudiants ORDER BY id")
        rows = cur.fetchall()
        conn.close()
        export_query_to_xlsx(["id", "matricule", "nom", "prenom", "email", "statut"], rows, path, "etudiants")
        messagebox.showinfo("OK", "Export Excel terminé.")

    # ACADEMIQUE

    def build_academique_tab(self):
        frm = ttk.Frame(self.tab_academique, padding=10)
        frm.pack(fill="both", expand=True)

        lf = ttk.LabelFrame(frm, text="Filières", padding=10)
        ln = ttk.LabelFrame(frm, text="Niveaux", padding=10)
        lf.pack(side="left", fill="both", expand=True, padx=(0, 10))
        ln.pack(side="left", fill="both", expand=True)

        ttk.Label(lf, text="Code").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Label(lf, text="Nom").grid(row=1, column=0, sticky="w", pady=4)
        self.f_code = ttk.Entry(lf, width=22)
        self.f_nom = ttk.Entry(lf, width=22)
        self.f_code.grid(row=0, column=1, pady=4)
        self.f_nom.grid(row=1, column=1, pady=4)
        ttk.Button(lf, text="Ajouter filière", command=self.add_filiere).grid(row=2, column=1, sticky="e", pady=(10, 0))

        self.list_filieres = tk.Listbox(lf, height=18, width=45)
        self.list_filieres.grid(row=3, column=0, columnspan=2, pady=(12, 0), sticky="nsew")

        ttk.Label(ln, text="Code").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Label(ln, text="Nom").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Label(ln, text="Ordre").grid(row=2, column=0, sticky="w", pady=4)
        self.n_code = ttk.Entry(ln, width=22)
        self.n_nom = ttk.Entry(ln, width=22)
        self.n_ordre = ttk.Entry(ln, width=22)
        self.n_code.grid(row=0, column=1, pady=4)
        self.n_nom.grid(row=1, column=1, pady=4)
        self.n_ordre.grid(row=2, column=1, pady=4)
        ttk.Button(ln, text="Ajouter niveau", command=self.add_niveau).grid(row=3, column=1, sticky="e", pady=(10, 0))

        self.list_niveaux = tk.Listbox(ln, height=18, width=45)
        self.list_niveaux.grid(row=4, column=0, columnspan=2, pady=(12, 0), sticky="nsew")

    def add_filiere(self):
        code = self.f_code.get().strip()
        nom = self.f_nom.get().strip()
        if not code or not nom:
            messagebox.showerror("Erreur", "Code et nom filière obligatoires.")
            return

        conn = db_connect()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO filieres (code, nom) VALUES (?, ?)", (code, nom))
            conn.commit()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erreur", "Code filière déjà utilisé.")
        finally:
            conn.close()

        self.f_code.delete(0, tk.END)
        self.f_nom.delete(0, tk.END)
        self.refresh_all()

    def add_niveau(self):
        code = self.n_code.get().strip()
        nom = self.n_nom.get().strip()
        ordre_txt = self.n_ordre.get().strip()

        if not code or not nom:
            messagebox.showerror("Erreur", "Code et nom niveau obligatoires.")
            return

        ordre = None
        if ordre_txt:
            if not ordre_txt.isdigit():
                messagebox.showerror("Erreur", "Ordre doit être un entier (ex: 4).")
                return
            ordre = int(ordre_txt)

        conn = db_connect()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO niveaux (code, nom, ordre) VALUES (?, ?, ?)", (code, nom, ordre))
            conn.commit()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erreur", "Code niveau déjà utilisé.")
        finally:
            conn.close()

        self.n_code.delete(0, tk.END)
        self.n_nom.delete(0, tk.END)
        self.n_ordre.delete(0, tk.END)
        self.refresh_all()

    def refresh_filieres(self):
        if not hasattr(self, "list_filieres"):
            return
        self.list_filieres.delete(0, tk.END)
        conn = db_connect()
        cur = conn.cursor()
        cur.execute("SELECT id, code, nom FROM filieres ORDER BY code")
        self._filieres = cur.fetchall()
        conn.close()

        for (fid, code, nom) in self._filieres:
            self.list_filieres.insert(tk.END, f"{fid} - {code} - {nom}")

        fil_values = [f"{fid} - {code} - {nom}" for (fid, code, nom) in self._filieres]
        if hasattr(self, "cb_filiere"): self.cb_filiere["values"] = fil_values
        if hasattr(self, "cb_mod_filiere"): self.cb_mod_filiere["values"] = fil_values

    def refresh_niveaux(self):
        if not hasattr(self, "list_niveaux"):
            return
        self.list_niveaux.delete(0, tk.END)
        conn = db_connect()
        cur = conn.cursor()
        cur.execute("SELECT id, code, nom, COALESCE(ordre,'') FROM niveaux ORDER BY COALESCE(ordre, 999), code")
        self._niveaux = cur.fetchall()
        conn.close()

        for (nid, code, nom, ordre) in self._niveaux:
            self.list_niveaux.insert(tk.END, f"{nid} - {code} - {nom} - ordre:{ordre}")

        niv_values = [f"{nid} - {code} - {nom}" for (nid, code, nom, _) in self._niveaux]
        if hasattr(self, "cb_niveau"): self.cb_niveau["values"] = niv_values
        if hasattr(self, "cb_mod_niveau"): self.cb_mod_niveau["values"] = niv_values

    # INSCRIPTIONS

    def build_inscriptions_tab(self):
        frm = ttk.Frame(self.tab_inscriptions, padding=10)
        frm.pack(fill="both", expand=True)

        top = ttk.LabelFrame(frm, text="Nouvelle inscription", padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="Étudiant").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Label(top, text="Filière").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Label(top, text="Niveau").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Label(top, text="Année académique").grid(row=3, column=0, sticky="w", pady=4)

        self.cb_etudiant = ttk.Combobox(top, width=70, state="readonly")
        self.cb_filiere = ttk.Combobox(top, width=70, state="readonly")
        self.cb_niveau = ttk.Combobox(top, width=70, state="readonly")
        self.e_annee = ttk.Entry(top, width=22)

        self.cb_etudiant.grid(row=0, column=1, padx=6, pady=4, sticky="w")
        self.cb_filiere.grid(row=1, column=1, padx=6, pady=4, sticky="w")
        self.cb_niveau.grid(row=2, column=1, padx=6, pady=4, sticky="w")
        self.e_annee.grid(row=3, column=1, padx=6, pady=4, sticky="w")

        ttk.Button(top, text="Enregistrer inscription", command=self.add_inscription)\
            .grid(row=4, column=1, sticky="e", pady=(10, 0))

        bottom = ttk.LabelFrame(frm, text="Historique des inscriptions", padding=10)
        bottom.pack(fill="both", expand=True, pady=(10, 0))

        cols = ("id", "matricule", "etudiant", "filiere", "niveau", "annee", "statut")
        self.tree_inscriptions = ttk.Treeview(bottom, columns=cols, show="headings", height=15)
        for c in cols:
            self.tree_inscriptions.heading(c, text=c)
            self.tree_inscriptions.column(c, width=140, anchor="w")
        self.tree_inscriptions.column("id", width=50, anchor="center")
        self.tree_inscriptions.column("annee", width=110, anchor="center")

        self.tree_inscriptions.pack(fill="both", expand=True)

    def refresh_inscriptions_lists(self):
        if not hasattr(self, "cb_etudiant"):
            return

        conn = db_connect()
        cur = conn.cursor()
        cur.execute("SELECT id, matricule, nom, prenom FROM etudiants ORDER BY nom, prenom")
        self._etudiants = cur.fetchall()
        conn.close()

        vals_etu = [f"{eid} - {mat} - {nom} {prenom}" for (eid, mat, nom, prenom) in self._etudiants]
        self.cb_etudiant["values"] = vals_etu
        if hasattr(self, "cb_note_etudiant"): self.cb_note_etudiant["values"] = vals_etu
        if hasattr(self, "cb_abs_etudiant"): self.cb_abs_etudiant["values"] = vals_etu
        if hasattr(self, "cb_doc_etudiant"): self.cb_doc_etudiant["values"] = vals_etu

        if hasattr(self, "tree_inscriptions"):
            for row in self.tree_inscriptions.get_children():
                self.tree_inscriptions.delete(row)

            conn = db_connect()
            cur = conn.cursor()
            cur.execute("""
                SELECT i.id,
                       e.matricule,
                       e.nom || ' ' || e.prenom AS etu,
                       f.code || ' - ' || f.nom AS fil,
                       n.code || ' - ' || n.nom AS niv,
                       i.annee_academique,
                       COALESCE(i.statut,'')
                FROM inscriptions i
                JOIN etudiants e ON e.id = i.etudiant_id
                JOIN filieres f  ON f.id = i.filiere_id
                JOIN niveaux n   ON n.id = i.niveau_id
                ORDER BY i.id DESC
            """)
            rows = cur.fetchall()
            conn.close()

            for r in rows:
                self.tree_inscriptions.insert("", "end", values=r)

    def add_inscription(self):
        etu_id = self.parse_id_from_combo(self.cb_etudiant.get())
        filiere_id = self.parse_id_from_combo(self.cb_filiere.get())
        niveau_id = self.parse_id_from_combo(self.cb_niveau.get())
        annee = self.e_annee.get().strip()

        if not (etu_id and filiere_id and niveau_id and annee):
            messagebox.showerror("Erreur", "Étudiant, filière, niveau et année sont obligatoires.")
            return

        conn = db_connect()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO inscriptions (etudiant_id, filiere_id, niveau_id, annee_academique, statut)
            VALUES (?, ?, ?, ?, ?)
        """, (etu_id, filiere_id, niveau_id, annee, "inscrit"))
        conn.commit()
        conn.close()

        self.refresh_inscriptions_lists()
        messagebox.showinfo("OK", "Inscription enregistrée.")

    # MODULES & NOTES

    def build_notes_tab(self):
        frm = ttk.Frame(self.tab_notes, padding=10)
        frm.pack(fill="both", expand=True)

        left = ttk.LabelFrame(frm, text="Modules", padding=10)
        left.pack(side="left", fill="y", padx=(0, 10))

        ttk.Label(left, text="Code").grid(row=0, column=0, sticky="w", pady=3)
        ttk.Label(left, text="Nom").grid(row=1, column=0, sticky="w", pady=3)
        ttk.Label(left, text="Coefficient").grid(row=2, column=0, sticky="w", pady=3)
        ttk.Label(left, text="Crédits").grid(row=3, column=0, sticky="w", pady=3)
        ttk.Label(left, text="Filière").grid(row=4, column=0, sticky="w", pady=3)
        ttk.Label(left, text="Niveau").grid(row=5, column=0, sticky="w", pady=3)

        self.e_mod_code = ttk.Entry(left, width=24)
        self.e_mod_nom = ttk.Entry(left, width=24)
        self.e_mod_coef = ttk.Entry(left, width=24)
        self.e_mod_credits = ttk.Entry(left, width=24)

        self.cb_mod_filiere = ttk.Combobox(left, width=40, state="readonly")
        self.cb_mod_niveau = ttk.Combobox(left, width=40, state="readonly")

        self.e_mod_code.grid(row=0, column=1, pady=3, sticky="w")
        self.e_mod_nom.grid(row=1, column=1, pady=3, sticky="w")
        self.e_mod_coef.grid(row=2, column=1, pady=3, sticky="w")
        self.e_mod_credits.grid(row=3, column=1, pady=3, sticky="w")
        self.cb_mod_filiere.grid(row=4, column=1, pady=3, sticky="w")
        self.cb_mod_niveau.grid(row=5, column=1, pady=3, sticky="w")

        ttk.Button(left, text="Ajouter module", command=self.add_module).grid(row=6, column=1, sticky="e", pady=(8, 0))

        self.list_modules = tk.Listbox(left, height=12, width=62)
        self.list_modules.grid(row=7, column=0, columnspan=2, pady=(10, 0), sticky="nsew")

        right = ttk.LabelFrame(frm, text="Notes", padding=10)
        right.pack(side="left", fill="both", expand=True)

        top = ttk.Frame(right)
        top.pack(fill="x")

        ttk.Label(top, text="Étudiant").grid(row=0, column=0, sticky="w", pady=3)
        ttk.Label(top, text="Module").grid(row=1, column=0, sticky="w", pady=3)
        ttk.Label(top, text="Note (0-20)").grid(row=2, column=0, sticky="w", pady=3)
        ttk.Label(top, text="Type").grid(row=3, column=0, sticky="w", pady=3)
        ttk.Label(top, text="Année").grid(row=4, column=0, sticky="w", pady=3)

        self.cb_note_etudiant = ttk.Combobox(top, width=60, state="readonly")
        self.cb_note_module = ttk.Combobox(top, width=60, state="readonly")
        self.e_note = ttk.Entry(top, width=18)
        self.e_type = ttk.Entry(top, width=18)
        self.e_note_annee = ttk.Entry(top, width=18)

        self.cb_note_etudiant.grid(row=0, column=1, padx=6, pady=3, sticky="w")
        self.cb_note_module.grid(row=1, column=1, padx=6, pady=3, sticky="w")
        self.e_note.grid(row=2, column=1, padx=6, pady=3, sticky="w")
        self.e_type.grid(row=3, column=1, padx=6, pady=3, sticky="w")
        self.e_note_annee.grid(row=4, column=1, padx=6, pady=3, sticky="w")

        btns = ttk.Frame(top)
        btns.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        ttk.Button(btns, text="Calculer moyenne", command=self.compute_moyenne).pack(side="left")
        ttk.Button(btns, text="Enregistrer note", command=self.add_note).pack(side="right", padx=6)
        ttk.Button(btns, text="Modifier note", command=self.update_note_selected).pack(side="right", padx=6)
        ttk.Button(btns, text="Supprimer note", command=self.delete_note_selected).pack(side="right", padx=6)

        self.lbl_moyenne = ttk.Label(top, text="Moyenne: -")
        self.lbl_moyenne.grid(row=6, column=0, columnspan=2, sticky="w", pady=(8, 0))

        bottom = ttk.Frame(right)
        bottom.pack(fill="both", expand=True, pady=(10, 0))

        cols = ("id", "etudiant", "module", "note", "coef", "annee", "type")
        self.tree_notes = ttk.Treeview(bottom, columns=cols, show="headings", height=12)
        for c in cols:
            self.tree_notes.heading(c, text=c)
            self.tree_notes.column(c, width=150, anchor="w")
        self.tree_notes.column("id", width=60, anchor="center")
        self.tree_notes.column("note", width=80, anchor="center")
        self.tree_notes.column("coef", width=70, anchor="center")
        self.tree_notes.pack(fill="both", expand=True)

        audit_box = ttk.LabelFrame(right, text="Traçabilité (notes_audit)", padding=10)
        audit_box.pack(fill="both", expand=False, pady=(8, 0))
        self.tree_audit = ttk.Treeview(audit_box, columns=("id", "action", "old", "new", "at", "by"), show="headings", height=6)
        for c, w in [("id", 60), ("action", 80), ("old", 240), ("new", 240), ("at", 160), ("by", 120)]:
            self.tree_audit.heading(c, text=c)
            self.tree_audit.column(c, width=w, anchor="w")
        self.tree_audit.column("id", width=60, anchor="center")
        self.tree_audit.pack(fill="both", expand=True)

        self.tree_notes.bind("<<TreeviewSelect>>", self.refresh_audit_for_selected_note)

    def add_module(self):
        code = self.e_mod_code.get().strip()
        nom = self.e_mod_nom.get().strip()
        coef_txt = self.e_mod_coef.get().strip()
        credits_txt = self.e_mod_credits.get().strip()
        filiere_id = self.parse_id_from_combo(self.cb_mod_filiere.get())
        niveau_id = self.parse_id_from_combo(self.cb_mod_niveau.get())

        if not code or not nom or not coef_txt:
            messagebox.showerror("Erreur", "Code, nom et coefficient sont obligatoires.")
            return

        try:
            coef = float(coef_txt.replace(",", "."))
        except ValueError:
            messagebox.showerror("Erreur", "Coefficient invalide (ex: 2 ou 1.5).")
            return

        credits = None
        if credits_txt:
            if not credits_txt.isdigit():
                messagebox.showerror("Erreur", "Crédits doit être un entier (ex: 5).")
                return
            credits = int(credits_txt)

        conn = db_connect()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO modules (code, nom, coefficient, credits, filiere_id, niveau_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (code, nom, coef, credits, filiere_id, niveau_id))
            conn.commit()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erreur", "Code module déjà utilisé.")
        finally:
            conn.close()

        self.e_mod_code.delete(0, tk.END)
        self.e_mod_nom.delete(0, tk.END)
        self.e_mod_coef.delete(0, tk.END)
        self.e_mod_credits.delete(0, tk.END)

        self.refresh_all()

    def refresh_modules_list(self):
        if not hasattr(self, "list_modules"):
            return
        self.list_modules.delete(0, tk.END)

        conn = db_connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT m.id, m.code, m.nom, m.coefficient,
                   COALESCE(f.code,''), COALESCE(n.code,'')
            FROM modules m
            LEFT JOIN filieres f ON f.id = m.filiere_id
            LEFT JOIN niveaux n  ON n.id = m.niveau_id
            ORDER BY m.code
        """)
        self._modules = cur.fetchall()
        conn.close()

        for (mid, code, nom, coef, fcode, ncode) in self._modules:
            tag = f"{fcode}/{ncode}" if (fcode or ncode) else ""
            self.list_modules.insert(tk.END, f"{mid} - {code} - {nom} (coef={coef}) {tag}")

        vals_mod = [f"{mid} - {code} - {nom}" for (mid, code, nom, _, _, _) in self._modules]
        if hasattr(self, "cb_note_module"): self.cb_note_module["values"] = vals_mod
        if hasattr(self, "cb_abs_module"): self.cb_abs_module["values"] = vals_mod
        if hasattr(self, "cb_aff_module"): self.cb_aff_module["values"] = vals_mod

    def add_note(self):
        etu_id = self.parse_id_from_combo(self.cb_note_etudiant.get())
        mod_id = self.parse_id_from_combo(self.cb_note_module.get())
        note_txt = self.e_note.get().strip()
        typ = self.e_type.get().strip()
        annee = self.e_note_annee.get().strip()

        if not (etu_id and mod_id and note_txt):
            messagebox.showerror("Erreur", "Étudiant, module et note sont obligatoires.")
            return

        try:
            note = float(note_txt.replace(",", "."))
        except ValueError:
            messagebox.showerror("Erreur", "Note invalide (ex: 14.5).")
            return

        if note < 0 or note > 20:
            messagebox.showerror("Erreur", "La note doit être entre 0 et 20.")
            return

        conn = db_connect()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO notes (etudiant_id, module_id, note, type_evaluation, annee_academique)
            VALUES (?, ?, ?, ?, ?)
        """, (etu_id, mod_id, note, typ if typ else None, annee if annee else None))
        note_id = cur.lastrowid

        cur.execute("""
            INSERT INTO notes_audit (note_id, action, old_value, new_value, changed_at, changed_by)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (note_id, "INSERT", None, f"note={note};type={typ};annee={annee}", now_iso(), self.username))

        conn.commit()
        conn.close()

        self.e_note.delete(0, tk.END)
        self.e_type.delete(0, tk.END)
        self.refresh_notes_lists()
        messagebox.showinfo("OK", "Note enregistrée.")

    def _selected_note_id(self):
        sel = self.tree_notes.selection()
        if not sel:
            return None
        values = self.tree_notes.item(sel[0], "values")
        return int(values[0])

    def update_note_selected(self):
        note_id = self._selected_note_id()
        if not note_id:
            messagebox.showerror("Erreur", "Sélectionne une note dans la table.")
            return

        note_txt = self.e_note.get().strip()
        typ = self.e_type.get().strip()
        annee = self.e_note_annee.get().strip()

        if not note_txt:
            messagebox.showerror("Erreur", "Saisis une nouvelle note dans le champ Note.")
            return

        try:
            note = float(note_txt.replace(",", "."))
        except ValueError:
            messagebox.showerror("Erreur", "Note invalide (ex: 14.5).")
            return

        if note < 0 or note > 20:
            messagebox.showerror("Erreur", "La note doit être entre 0 et 20.")
            return

        conn = db_connect()
        cur = conn.cursor()
        cur.execute("SELECT note, COALESCE(type_evaluation,''), COALESCE(annee_academique,'') FROM notes WHERE id=?", (note_id,))
        old = cur.fetchone()
        if not old:
            conn.close()
            messagebox.showerror("Erreur", "Note introuvable.")
            return

        cur.execute("""
            UPDATE notes
            SET note=?, type_evaluation=?, annee_academique=?
            WHERE id=?
        """, (note, typ if typ else None, annee if annee else None, note_id))

        cur.execute("""
            INSERT INTO notes_audit (note_id, action, old_value, new_value, changed_at, changed_by)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            note_id,
            "UPDATE",
            f"note={old[0]};type={old[1]};annee={old[2]}",
            f"note={note};type={typ};annee={annee}",
            now_iso(),
            self.username
        ))

        conn.commit()
        conn.close()

        self.refresh_notes_lists()
        self.refresh_audit_for_selected_note()
        messagebox.showinfo("OK", "Note modifiée (traçabilité enregistrée).")

    def delete_note_selected(self):
        note_id = self._selected_note_id()
        if not note_id:
            messagebox.showerror("Erreur", "Sélectionne une note dans la table.")
            return
        if not messagebox.askyesno("Confirmer", "Supprimer la note sélectionnée ?"):
            return

        conn = db_connect()
        cur = conn.cursor()
        cur.execute("SELECT note, COALESCE(type_evaluation,''), COALESCE(annee_academique,'') FROM notes WHERE id=?", (note_id,))
        old = cur.fetchone()

        cur.execute("""
            INSERT INTO notes_audit (note_id, action, old_value, new_value, changed_at, changed_by)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            note_id,
            "DELETE",
            f"note={old[0]};type={old[1]};annee={old[2]}" if old else None,
            None,
            now_iso(),
            self.username
        ))

        cur.execute("DELETE FROM notes WHERE id=?", (note_id,))
        conn.commit()
        conn.close()

        self.refresh_notes_lists()
        for r in self.tree_audit.get_children():
            self.tree_audit.delete(r)
        messagebox.showinfo("OK", "Note supprimée.")

    def refresh_notes_lists(self):
        if not hasattr(self, "tree_notes"):
            return
        for row in self.tree_notes.get_children():
            self.tree_notes.delete(row)

        conn = db_connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT no.id,
                   e.matricule || ' - ' || e.nom || ' ' || e.prenom AS etu,
                   m.code || ' - ' || m.nom AS mod,
                   no.note,
                   m.coefficient,
                   COALESCE(no.annee_academique,''),
                   COALESCE(no.type_evaluation,'')
            FROM notes no
            JOIN etudiants e ON e.id = no.etudiant_id
            JOIN modules m   ON m.id = no.module_id
            ORDER BY no.id DESC
        """)
        rows = cur.fetchall()
        conn.close()

        for r in rows:
            self.tree_notes.insert("", "end", values=r)

    def refresh_audit_for_selected_note(self, event=None):
        note_id = self._selected_note_id()
        if not note_id:
            return
        for row in self.tree_audit.get_children():
            self.tree_audit.delete(row)

        conn = db_connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, action, COALESCE(old_value,''), COALESCE(new_value,''), COALESCE(changed_at,''), COALESCE(changed_by,'')
            FROM notes_audit
            WHERE note_id=?
            ORDER BY id DESC
        """, (note_id,))
        rows = cur.fetchall()
        conn.close()

        for r in rows:
            self.tree_audit.insert("", "end", values=r)

    def compute_moyenne(self):
        etu_id = self.parse_id_from_combo(self.cb_note_etudiant.get())
        if not etu_id:
            messagebox.showerror("Erreur", "Choisis un étudiant.")
            return

        conn = db_connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT SUM(no.note * m.coefficient) AS total_points,
                   SUM(m.coefficient) AS total_coef
            FROM notes no
            JOIN modules m ON m.id = no.module_id
            WHERE no.etudiant_id = ?
        """, (etu_id,))
        row = cur.fetchone()
        conn.close()

        if not row or row[0] is None or row[1] is None or row[1] == 0:
            self.lbl_moyenne.config(text="Moyenne: - (aucune note)")
            return

        moyenne = row[0] / row[1]
        self.lbl_moyenne.config(text=f"Moyenne: {moyenne:.2f} / 20")

    # ABSENCES

    def build_absences_tab(self):
        frm = ttk.Frame(self.tab_absences, padding=10)
        frm.pack(fill="both", expand=True)

        top = ttk.LabelFrame(frm, text="Enregistrer une absence", padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="Étudiant").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Label(top, text="Module").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Label(top, text="Date (YYYY-MM-DD)").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Label(top, text="Justifiée").grid(row=3, column=0, sticky="w", pady=4)
        ttk.Label(top, text="Motif").grid(row=4, column=0, sticky="w", pady=4)

        self.cb_abs_etudiant = ttk.Combobox(top, width=60, state="readonly")
        self.cb_abs_module = ttk.Combobox(top, width=60, state="readonly")
        self.e_abs_date = ttk.Entry(top, width=20)
        self.var_justifiee = tk.IntVar()
        self.chk_just = ttk.Checkbutton(top, variable=self.var_justifiee)
        self.e_abs_motif = ttk.Entry(top, width=40)

        self.cb_abs_etudiant.grid(row=0, column=1, pady=4, sticky="w")
        self.cb_abs_module.grid(row=1, column=1, pady=4, sticky="w")
        self.e_abs_date.grid(row=2, column=1, pady=4, sticky="w")
        self.chk_just.grid(row=3, column=1, pady=4, sticky="w")
        self.e_abs_motif.grid(row=4, column=1, pady=4, sticky="w")

        ttk.Button(top, text="Enregistrer absence", command=self.add_absence)\
            .grid(row=5, column=1, sticky="e", pady=8)

        bottom = ttk.LabelFrame(frm, text="Historique des absences", padding=10)
        bottom.pack(fill="both", expand=True, pady=(10, 0))

        cols = ("id", "etudiant", "module", "date", "justifiee", "motif")
        self.tree_absences = ttk.Treeview(bottom, columns=cols, show="headings", height=14)
        for c in cols:
            self.tree_absences.heading(c, text=c)
            self.tree_absences.column(c, width=160, anchor="w")
        self.tree_absences.column("id", width=60, anchor="center")
        self.tree_absences.pack(fill="both", expand=True)

        ana = ttk.LabelFrame(frm, text="Analyse absences", padding=10)
        ana.pack(fill="x", pady=(10, 0))

        ttk.Label(ana, text="Seuil alerte (nb absences)").grid(row=0, column=0, sticky="w")
        self.e_abs_seuil = ttk.Entry(ana, width=10)
        self.e_abs_seuil.insert(0, "3")
        self.e_abs_seuil.grid(row=0, column=1, padx=8)

        ttk.Button(ana, text="Afficher alertes", command=self.show_absence_alerts).grid(row=0, column=2, padx=6)
        self.lbl_abs_stats = ttk.Label(ana, text="Taux: - | Alertes: -")
        self.lbl_abs_stats.grid(row=0, column=3, padx=10, sticky="w")

    def add_absence(self):
        etu_id = self.parse_id_from_combo(self.cb_abs_etudiant.get())
        mod_id = self.parse_id_from_combo(self.cb_abs_module.get())
        date_abs = self.e_abs_date.get().strip()
        just = self.var_justifiee.get()
        motif = self.e_abs_motif.get().strip()

        if not (etu_id and mod_id and date_abs):
            messagebox.showerror("Erreur", "Étudiant, module et date obligatoires.")
            return

        conn = db_connect()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO absences (etudiant_id, module_id, date_absence, justifiee, motif)
            VALUES (?, ?, ?, ?, ?)
        """, (etu_id, mod_id, date_abs, just, motif if motif else None))
        conn.commit()
        conn.close()

        self.refresh_absences()
        messagebox.showinfo("OK", "Absence enregistrée.")

    def refresh_absences(self):
        if not hasattr(self, "tree_absences"):
            return

        for row in self.tree_absences.get_children():
            self.tree_absences.delete(row)

        conn = db_connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT a.id,
                   e.nom || ' ' || e.prenom,
                   m.code || ' - ' || m.nom,
                   a.date_absence,
                   CASE a.justifiee WHEN 1 THEN 'Oui' ELSE 'Non' END,
                   COALESCE(a.motif,'')
            FROM absences a
            JOIN etudiants e ON e.id = a.etudiant_id
            JOIN modules m ON m.id = a.module_id
            ORDER BY a.date_absence DESC
        """)
        rows = cur.fetchall()

        cur.execute("SELECT COUNT(*) FROM absences")
        total_abs = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM etudiants")
        nb_etu = cur.fetchone()[0]

        conn.close()

        for r in rows:
            self.tree_absences.insert("", "end", values=r)

        taux = (total_abs / nb_etu) if nb_etu else 0.0
        self.lbl_abs_stats.config(text=f"Taux: {taux:.2f} abs/étudiant | Alertes: -")

    def show_absence_alerts(self):
        try:
            seuil = int(self.e_abs_seuil.get().strip())
        except ValueError:
            messagebox.showerror("Erreur", "Seuil invalide.")
            return

        conn = db_connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT e.matricule, e.nom || ' ' || e.prenom, COUNT(*) as nb
            FROM absences a
            JOIN etudiants e ON e.id=a.etudiant_id
            GROUP BY a.etudiant_id
            HAVING nb >= ?
            ORDER BY nb DESC
        """, (seuil,))
        rows = cur.fetchall()
        conn.close()

        if not rows:
            messagebox.showinfo("Alertes", "Aucune alerte.")
            t = self.lbl_abs_stats.cget("text").split("|")[0].strip()
            self.lbl_abs_stats.config(text=f"{t} | Alertes: 0")
            return

        txt = "\n".join([f"{m} - {n} : {k} absence(s)" for m, n, k in rows])
        messagebox.showinfo("Alertes absences", txt)
        t = self.lbl_abs_stats.cget("text").split("|")[0].strip()
        self.lbl_abs_stats.config(text=f"{t} | Alertes: {len(rows)}")

    # ENSEIGNANTS

    def build_enseignants_tab(self):
        frm = ttk.Frame(self.tab_enseignants, padding=10)
        frm.pack(fill="both", expand=True)

        left = ttk.LabelFrame(frm, text="Ajouter enseignant", padding=10)
        left.pack(side="left", fill="y", padx=(0, 10))

        ttk.Label(left, text="Nom").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Label(left, text="Prénom").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Label(left, text="Email").grid(row=2, column=0, sticky="w", pady=4)

        self.e_ens_nom = ttk.Entry(left, width=26)
        self.e_ens_pre = ttk.Entry(left, width=26)
        self.e_ens_mail = ttk.Entry(left, width=26)

        self.e_ens_nom.grid(row=0, column=1, pady=4)
        self.e_ens_pre.grid(row=1, column=1, pady=4)
        self.e_ens_mail.grid(row=2, column=1, pady=4)

        ttk.Button(left, text="Ajouter", command=self.add_enseignant).grid(row=3, column=1, sticky="e", pady=8)

        ttk.Separator(left, orient="horizontal").grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)

        ttk.Label(left, text="Affecter un module").grid(row=5, column=0, columnspan=2, sticky="w")
        ttk.Label(left, text="Enseignant").grid(row=6, column=0, sticky="w", pady=4)
        ttk.Label(left, text="Module").grid(row=7, column=0, sticky="w", pady=4)
        ttk.Label(left, text="Année").grid(row=8, column=0, sticky="w", pady=4)

        self.cb_aff_ens = ttk.Combobox(left, width=40, state="readonly")
        self.cb_aff_module = ttk.Combobox(left, width=40, state="readonly")
        self.e_aff_annee = ttk.Entry(left, width=18)

        self.cb_aff_ens.grid(row=6, column=1, pady=4, sticky="w")
        self.cb_aff_module.grid(row=7, column=1, pady=4, sticky="w")
        self.e_aff_annee.grid(row=8, column=1, pady=4, sticky="w")

        ttk.Button(left, text="Affecter", command=self.add_affectation).grid(row=9, column=1, sticky="e", pady=6)

        right = ttk.LabelFrame(frm, text="Enseignants & affectations", padding=10)
        right.pack(side="left", fill="both", expand=True)

        cols = ("id", "nom", "prenom", "email")
        self.tree_ens = ttk.Treeview(right, columns=cols, show="headings", height=12)
        for c in cols:
            self.tree_ens.heading(c, text=c)
            self.tree_ens.column(c, width=200, anchor="w")
        self.tree_ens.column("id", width=60, anchor="center")
        self.tree_ens.pack(fill="x", expand=False)

        cols2 = ("id", "enseignant", "module", "annee")
        self.tree_aff = ttk.Treeview(right, columns=cols2, show="headings", height=10)
        for c in cols2:
            self.tree_aff.heading(c, text=c)
            self.tree_aff.column(c, width=260, anchor="w")
        self.tree_aff.column("id", width=60, anchor="center")
        self.tree_aff.pack(fill="both", expand=True, pady=(10, 0))

    def add_enseignant(self):
        nom = self.e_ens_nom.get().strip()
        prenom = self.e_ens_pre.get().strip()
        email = self.e_ens_mail.get().strip() or None

        if not nom or not prenom:
            messagebox.showerror("Erreur", "Nom et prénom obligatoires.")
            return

        conn = db_connect()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO enseignants (nom, prenom, email) VALUES (?, ?, ?)", (nom, prenom, email))
            conn.commit()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erreur", "Email déjà utilisé.")
        finally:
            conn.close()

        self.e_ens_nom.delete(0, tk.END)
        self.e_ens_pre.delete(0, tk.END)
        self.e_ens_mail.delete(0, tk.END)
        self.refresh_enseignants()

    def add_affectation(self):
        ens_id = self.parse_id_from_combo(self.cb_aff_ens.get())
        mod_id = self.parse_id_from_combo(self.cb_aff_module.get())
        annee = self.e_aff_annee.get().strip() or None

        if not ens_id or not mod_id:
            messagebox.showerror("Erreur", "Enseignant et module obligatoires.")
            return

        conn = db_connect()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO enseignements (enseignant_id, module_id, annee_academique)
                VALUES (?, ?, ?)
            """, (ens_id, mod_id, annee))
            conn.commit()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erreur", "Affectation déjà existante.")
        finally:
            conn.close()

        self.refresh_enseignants()
        messagebox.showinfo("OK", "Affectation enregistrée.")

    def refresh_enseignants(self):
        if not hasattr(self, "tree_ens"):
            return

        for r in self.tree_ens.get_children():
            self.tree_ens.delete(r)
        for r in self.tree_aff.get_children():
            self.tree_aff.delete(r)

        conn = db_connect()
        cur = conn.cursor()
        cur.execute("SELECT id, nom, prenom, COALESCE(email,'') FROM enseignants ORDER BY nom, prenom")
        ens = cur.fetchall()

        vals_ens = [f"{eid} - {n} {p}" for (eid, n, p, _) in ens]
        self.cb_aff_ens["values"] = vals_ens

        for row in ens:
            self.tree_ens.insert("", "end", values=row)

        cur.execute("""
            SELECT en.id,
                   e.nom || ' ' || e.prenom,
                   m.code || ' - ' || m.nom,
                   COALESCE(en.annee_academique,'')
            FROM enseignements en
            JOIN enseignants e ON e.id=en.enseignant_id
            JOIN modules m ON m.id=en.module_id
            ORDER BY en.id DESC
        """)
        aff = cur.fetchall()
        conn.close()

        for row in aff:
            self.tree_aff.insert("", "end", values=row)

    # CALENDRIER

    def build_calendrier_tab(self):
        frm = ttk.Frame(self.tab_calendrier, padding=10)
        frm.pack(fill="both", expand=True)

        left = ttk.LabelFrame(frm, text="Semestres", padding=10)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        ttk.Label(left, text="Code (ex: S1)").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Label(left, text="Libellé").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Label(left, text="Début (YYYY-MM-DD)").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Label(left, text="Fin (YYYY-MM-DD)").grid(row=3, column=0, sticky="w", pady=4)

        self.e_sem_code = ttk.Entry(left, width=18)
        self.e_sem_lib = ttk.Entry(left, width=28)
        self.e_sem_deb = ttk.Entry(left, width=18)
        self.e_sem_fin = ttk.Entry(left, width=18)

        self.e_sem_code.grid(row=0, column=1, pady=4, sticky="w")
        self.e_sem_lib.grid(row=1, column=1, pady=4, sticky="w")
        self.e_sem_deb.grid(row=2, column=1, pady=4, sticky="w")
        self.e_sem_fin.grid(row=3, column=1, pady=4, sticky="w")

        ttk.Button(left, text="Ajouter semestre", command=self.add_semestre).grid(row=4, column=1, sticky="e", pady=8)

        self.tree_sem = ttk.Treeview(left, columns=("id", "code", "lib", "deb", "fin"), show="headings", height=10)
        for c, w in [("id", 60), ("code", 80), ("lib", 220), ("deb", 120), ("fin", 120)]:
            self.tree_sem.heading(c, text=c)
            self.tree_sem.column(c, width=w, anchor="w")
        self.tree_sem.column("id", width=60, anchor="center")
        self.tree_sem.grid(row=5, column=0, columnspan=2, sticky="nsew", pady=(10, 0))

        right = ttk.LabelFrame(frm, text="Périodes (cours/examens/vacances)", padding=10)
        right.pack(side="left", fill="both", expand=True)

        ttk.Label(right, text="Semestre").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Label(right, text="Type").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Label(right, text="Libellé").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Label(right, text="Début").grid(row=3, column=0, sticky="w", pady=4)
        ttk.Label(right, text="Fin").grid(row=4, column=0, sticky="w", pady=4)

        self.cb_per_sem = ttk.Combobox(right, width=40, state="readonly")
        self.e_per_type = ttk.Entry(right, width=20)
        self.e_per_lib = ttk.Entry(right, width=28)
        self.e_per_deb = ttk.Entry(right, width=18)
        self.e_per_fin = ttk.Entry(right, width=18)

        self.cb_per_sem.grid(row=0, column=1, pady=4, sticky="w")
        self.e_per_type.grid(row=1, column=1, pady=4, sticky="w")
        self.e_per_lib.grid(row=2, column=1, pady=4, sticky="w")
        self.e_per_deb.grid(row=3, column=1, pady=4, sticky="w")
        self.e_per_fin.grid(row=4, column=1, pady=4, sticky="w")

        ttk.Button(right, text="Ajouter période", command=self.add_periode).grid(row=5, column=1, sticky="e", pady=8)

        self.tree_per = ttk.Treeview(right, columns=("id", "sem", "type", "lib", "deb", "fin"), show="headings", height=10)
        for c, w in [("id", 60), ("sem", 120), ("type", 120), ("lib", 220), ("deb", 110), ("fin", 110)]:
            self.tree_per.heading(c, text=c)
            self.tree_per.column(c, width=w, anchor="w")
        self.tree_per.column("id", width=60, anchor="center")
        self.tree_per.grid(row=6, column=0, columnspan=2, sticky="nsew", pady=(10, 0))

    def add_semestre(self):
        code = self.e_sem_code.get().strip()
        lib = self.e_sem_lib.get().strip() or None
        deb = self.e_sem_deb.get().strip()
        fin = self.e_sem_fin.get().strip()

        if not code or not deb or not fin:
            messagebox.showerror("Erreur", "Code + dates début/fin obligatoires.")
            return

        conn = db_connect()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO semestres (code, libelle, date_debut, date_fin) VALUES (?, ?, ?, ?)", (code, lib, deb, fin))
            conn.commit()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erreur", "Code semestre déjà utilisé.")
        finally:
            conn.close()

        self.e_sem_code.delete(0, tk.END)
        self.e_sem_lib.delete(0, tk.END)
        self.e_sem_deb.delete(0, tk.END)
        self.e_sem_fin.delete(0, tk.END)
        self.refresh_calendrier()

    def add_periode(self):
        sem_id = self.parse_id_from_combo(self.cb_per_sem.get())
        typ = self.e_per_type.get().strip()
        lib = self.e_per_lib.get().strip() or None
        deb = self.e_per_deb.get().strip()
        fin = self.e_per_fin.get().strip()

        if not sem_id or not typ or not deb or not fin:
            messagebox.showerror("Erreur", "Semestre + type + dates obligatoires.")
            return

        conn = db_connect()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO periodes (semestre_id, type, libelle, date_debut, date_fin)
            VALUES (?, ?, ?, ?, ?)
        """, (sem_id, typ, lib, deb, fin))
        conn.commit()
        conn.close()

        self.e_per_type.delete(0, tk.END)
        self.e_per_lib.delete(0, tk.END)
        self.e_per_deb.delete(0, tk.END)
        self.e_per_fin.delete(0, tk.END)
        self.refresh_calendrier()

    def refresh_calendrier(self):
        if not hasattr(self, "tree_sem"):
            return
        for r in self.tree_sem.get_children():
            self.tree_sem.delete(r)
        for r in self.tree_per.get_children():
            self.tree_per.delete(r)

        conn = db_connect()
        cur = conn.cursor()

        cur.execute("SELECT id, code, COALESCE(libelle,''), date_debut, date_fin FROM semestres ORDER BY date_debut")
        sem = cur.fetchall()
        for row in sem:
            self.tree_sem.insert("", "end", values=row)

        self.cb_per_sem["values"] = [f"{sid} - {code} ({deb}→{fin})" for (sid, code, _, deb, fin) in sem]

        cur.execute("""
            SELECT p.id, s.code, p.type, COALESCE(p.libelle,''), p.date_debut, p.date_fin
            FROM periodes p
            JOIN semestres s ON s.id=p.semestre_id
            ORDER BY p.date_debut
        """)
        per = cur.fetchall()
        conn.close()

        for row in per:
            self.tree_per.insert("", "end", values=row)

    # DASHBOARD

    def build_dashboard_tab(self):
        frm = ttk.Frame(self.tab_dashboard, padding=10)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Dashboard", font=("Segoe UI", 14, "bold")).pack(anchor="w")

        self.lbl_kpis = ttk.Label(frm, text="", font=("Segoe UI", 11))
        self.lbl_kpis.pack(anchor="w", pady=(8, 10))

        box = ttk.LabelFrame(frm, text="Top absences", padding=10)
        box.pack(fill="both", expand=True)

        self.tree_top_abs = ttk.Treeview(box, columns=("matricule", "etudiant", "absences"), show="headings", height=12)
        for c, w in [("matricule", 180), ("etudiant", 360), ("absences", 120)]:
            self.tree_top_abs.heading(c, text=c)
            self.tree_top_abs.column(c, width=w, anchor="w")
        self.tree_top_abs.column("absences", width=120, anchor="center")
        self.tree_top_abs.pack(fill="both", expand=True)

        ttk.Button(frm, text="Rafraîchir", command=self.refresh_dashboard).pack(anchor="e", pady=(10, 0))

    def refresh_dashboard(self):
        if not hasattr(self, "lbl_kpis"):
            return

        conn = db_connect()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM etudiants")
        nb_etudiants = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM modules")
        nb_modules = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM inscriptions")
        nb_inscriptions = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM absences")
        nb_absences = cur.fetchone()[0]

        cur.execute("""
            SELECT e.matricule, e.nom || ' ' || e.prenom, COUNT(*) as nb
            FROM absences a
            JOIN etudiants e ON e.id=a.etudiant_id
            GROUP BY a.etudiant_id
            ORDER BY nb DESC
            LIMIT 5
        """)
        top_abs = cur.fetchall()
        conn.close()

        self.lbl_kpis.config(
            text=f"Étudiants: {nb_etudiants} | Modules: {nb_modules} | "
                 f"Inscriptions: {nb_inscriptions} | Absences: {nb_absences}"
        )

        for row in self.tree_top_abs.get_children():
            self.tree_top_abs.delete(row)
        for m, e, n in top_abs:
            self.tree_top_abs.insert("", "end", values=(m, e, n))

    # DOCUMENTS

    def build_documents_tab(self):
        frm = ttk.Frame(self.tab_documents, padding=10)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Documents & Exports", font=("Segoe UI", 14, "bold")).pack(anchor="w")

        line = ttk.Frame(frm)
        line.pack(fill="x", pady=10)
        ttk.Button(line, text="Exporter notes (Excel)", command=self.export_notes_xlsx).pack(side="left", padx=6)
        ttk.Button(line, text="Exporter absences (Excel)", command=self.export_absences_xlsx).pack(side="left", padx=6)

        ttk.Separator(frm, orient="horizontal").pack(fill="x", pady=10)

        pdf = ttk.LabelFrame(frm, text="PDF", padding=10)
        pdf.pack(fill="x")

        ttk.Label(pdf, text="Étudiant").grid(row=0, column=0, sticky="w")
        self.cb_doc_etudiant = ttk.Combobox(pdf, width=70, state="readonly")
        self.cb_doc_etudiant.grid(row=0, column=1, padx=8, pady=4, sticky="w")

        ttk.Button(pdf, text="Relevé PDF", command=self.export_releve_pdf).grid(row=1, column=1, sticky="e", padx=8, pady=6)

        att = ttk.Frame(pdf)
        att.grid(row=2, column=0, columnspan=2, sticky="w", pady=6)

        ttk.Label(att, text="Année (attestation)").grid(row=0, column=0, sticky="w")
        self.e_doc_annee = ttk.Entry(att, width=20)
        self.e_doc_annee.grid(row=0, column=1, padx=8, pady=4, sticky="w")
        ttk.Button(att, text="Attestation PDF", command=self.export_attestation_pdf).grid(row=0, column=2, padx=8)

    def refresh_documents_lists(self):
        # alimenté via refresh_inscriptions_lists (cb_doc_etudiant)
        pass

    def close_app(self):
        """Ferme l'application complètement"""
        self.destroy()
        if self.root:
            self.root.quit()
        else:
            import sys
            sys.exit(0)

    def export_releve_pdf(self):
        etu_id = self.parse_id_from_combo(self.cb_doc_etudiant.get())
        if not etu_id:
            messagebox.showerror("Erreur", "Choisis un étudiant.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not path:
            return
        conn = db_connect()
        try:
            generate_transcript_pdf(conn, etu_id, path)
        finally:
            conn.close()
        messagebox.showinfo("OK", "Relevé PDF généré.")

    def export_attestation_pdf(self):
        etu_id = self.parse_id_from_combo(self.cb_doc_etudiant.get())
        annee = self.e_doc_annee.get().strip()
        if not etu_id or not annee:
            messagebox.showerror("Erreur", "Étudiant et année obligatoires.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not path:
            return
        conn = db_connect()
        try:
            generate_attestation_pdf(conn, etu_id, annee, path)
        finally:
            conn.close()
        messagebox.showinfo("OK", "Attestation PDF générée.")

    def export_notes_xlsx(self):
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if not path:
            return
        conn = db_connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT no.id,
                   e.matricule,
                   e.nom || ' ' || e.prenom AS etudiant,
                   m.code,
                   m.nom AS module,
                   no.note,
                   m.coefficient,
                   COALESCE(no.annee_academique,'') AS annee,
                   COALESCE(no.type_evaluation,'') AS type
            FROM notes no
            JOIN etudiants e ON e.id=no.etudiant_id
            JOIN modules m ON m.id=no.module_id
            ORDER BY no.id
        """)
        rows = cur.fetchall()
        conn.close()

        export_query_to_xlsx(
            ["id", "matricule", "etudiant", "code_module", "module", "note", "coef", "annee", "type"],
            rows,
            path,
            "notes"
        )
        messagebox.showinfo("OK", "Export notes Excel terminé.")

    def export_absences_xlsx(self):
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if not path:
            return
        conn = db_connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT a.id,
                   e.matricule,
                   e.nom || ' ' || e.prenom AS etudiant,
                   m.code,
                   m.nom AS module,
                   a.date_absence,
                   a.justifiee,
                   COALESCE(a.motif,'')
            FROM absences a
            JOIN etudiants e ON e.id=a.etudiant_id
            JOIN modules m ON m.id=a.module_id
            ORDER BY a.id
        """)
        rows = cur.fetchall()
        conn.close()

        export_query_to_xlsx(
            ["id", "matricule", "etudiant", "code_module", "module", "date_absence", "justifiee", "motif"],
            rows,
            path,
            "absences"
        )
        messagebox.showinfo("OK", "Export absences Excel terminé.")


# LOGIN WINDOW

class Login(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Connexion")
        self.geometry("320x180")
        self.resizable(False, False)
        
        # Fermer l'application si on ferme la fenêtre de connexion
        self.protocol("WM_DELETE_WINDOW", self.close_app)

        frm = ttk.Frame(self, padding=12)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Utilisateur").grid(row=0, column=0, sticky="w", pady=6)
        ttk.Label(frm, text="Mot de passe").grid(row=1, column=0, sticky="w", pady=6)

        self.user = ttk.Entry(frm, width=26)
        self.pwd = ttk.Entry(frm, width=26, show="*")

        self.user.grid(row=0, column=1, pady=6)
        self.pwd.grid(row=1, column=1, pady=6)

        ttk.Button(frm, text="Se connecter", command=self.try_login).grid(row=2, column=1, sticky="e", pady=10)

    def close_app(self):
        """Ferme l'application complètement"""
        self.master.quit()

    def try_login(self):
        username = self.user.get().strip()
        password = self.pwd.get().strip()
        if not username or not password:
            messagebox.showerror("Erreur", "Champs manquants.")
            return

        conn = db_connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT role FROM users
            WHERE username = ? AND password_hash = ? AND actif = 1
        """, (username, hash_password(password)))
        row = cur.fetchone()
        conn.close()

        if not row:
            messagebox.showerror("Erreur", "Identifiants invalides.")
            return

        self.destroy()
        App(self.master, username=username, root=self.master)


# RUN 

if __name__ == "__main__":
    ensure_tables_and_seed()

    root = tk.Tk()
    root.withdraw()

    ttkb.Style(theme="flatly")

    Login(root)
    root.mainloop()
