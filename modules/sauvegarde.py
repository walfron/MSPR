import os
import sys
import csv
import mysql.connector
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# --- 1. CONFIGURATION ---
current_dir = Path(__file__).resolve().parent
env_path = current_dir.parent / '.env'
load_dotenv(dotenv_path=env_path)

DB_HOST = os.getenv("mysql_host")
DB_PORT = os.getenv("mysql_port")
DB_USER = os.getenv("mysql_user")
DB_PASS = os.getenv("mysql_password")
DB_NAME = os.getenv("mysql_database")

BACKUP_DIR = current_dir.parent / "backups"
os.makedirs(BACKUP_DIR, exist_ok=True)

# --- 2. FONCTIONS OUTILS ---

def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def list_tables():
    """Affiche la liste des tables disponibles dans la base"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        conn.close()
        
        print("\n--- TABLES DISPONIBLES ---")
        table_list = []
        for t in tables:
            print(f" - {t[0]}")
            table_list.append(t[0])
        print("--------------------------")
        return table_list
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")
        return []

# --- 3. FONCTIONS PRINCIPALES ---

def backup_sql_pure_python():
    """Génère un dump SQL sans utiliser mysqldump (Méthode Portable)"""
    print(f"\n[{get_timestamp()}] 🚀 Démarrage de la sauvegarde SQL (Mode Python)...")
    
    filename = f"FULL_BACKUP_{DB_NAME}_{get_timestamp()}.sql"
    filepath = BACKUP_DIR / filename

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"-- Sauvegarde automatique WMS\n-- Date: {get_timestamp()}\n\n")
            f.write(f"SET FOREIGN_KEY_CHECKS=0;\n\n")

            # Récupérer la liste des tables
            cursor.execute("SHOW TABLES")
            tables = [t[0] for t in cursor.fetchall()]

            for table in tables:
                print(f"   Traitement de la table : {table}")
                
                # 1. Structure de la table
                f.write(f"-- Structure de la table `{table}`\n")
                f.write(f"DROP TABLE IF EXISTS `{table}`;\n")
                
                cursor.execute(f"SHOW CREATE TABLE `{table}`")
                create_stmt = cursor.fetchone()[1]
                f.write(f"{create_stmt};\n\n")

                # 2. Données de la table
                cursor.execute(f"SELECT * FROM `{table}`")
                rows = cursor.fetchall()
                
                if rows:
                    f.write(f"-- Données de la table `{table}`\n")
                    f.write(f"INSERT INTO `{table}` VALUES \n")
                    
                    values_list = []
                    for row in rows:
                        # Nettoyage des données pour le SQL
                        clean_row = []
                        for val in row:
                            if val is None:
                                clean_row.append("NULL")
                            elif isinstance(val, (int, float)):
                                clean_row.append(str(val))
                            else:
                                # Échapper les guillemets simples
                                val_str = str(val).replace("'", "''").replace("\\", "\\\\")
                                clean_row.append(f"'{val_str}'")
                        
                        values_list.append("(" + ", ".join(clean_row) + ")")
                    
                    f.write(",\n".join(values_list) + ";\n\n")

            f.write("SET FOREIGN_KEY_CHECKS=1;\n")

        print(f"✅ Sauvegarde réussie : {filepath}")
        conn.close()

    except Exception as e:
        print(f"⛔ Erreur critique : {e}")

def export_table_to_csv():
    """Demande la table et l'exporte"""
    # On affiche d'abord les tables pour aider l'utilisateur
    available_tables = list_tables()
    
    if not available_tables:
        return

    table_name = input("\nEntrez le NOM EXACT de la table à exporter (parmi la liste ci-dessus) : ")
    
    if table_name not in available_tables:
        print("❌ Erreur : Cette table n'existe pas.")
        return

    print(f"\n[{get_timestamp()}] 📊 Export CSV de '{table_name}'...")
    filename = f"EXPORT_{table_name}_{get_timestamp()}.csv"
    filepath = BACKUP_DIR / filename

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT * FROM `{table_name}`")
        headers = [i[0] for i in cursor.description]
        rows = cursor.fetchall()

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)

        print(f"✅ Export réussi : {filepath}")
        conn.close()
    except Exception as e:
        print(f"❌ Erreur : {e}")

# --- 4. MENU ---

if __name__ == "__main__":
    while True:
        print("\n" + "="*40)
        print(" MODULE DE SAUVEGARDE WMS (Portable)")
        print("="*40)
        print("1. Sauvegarde Complète (SQL)")
        print("2. Export d'une table (CSV)")
        print("3. Quitter")
        
        choice = input("\nVotre choix : ")

        if choice == "1":
            backup_sql_pure_python()
        elif choice == "2":
            export_table_to_csv()
        elif choice == "3":
            print("Au revoir.")
            break
        else:
            print("Choix invalide.")