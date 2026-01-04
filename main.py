import sys
import os

# Import des modules
# Assurez-vous que le dossier 'modules' contient un fichier vide __init__.py 
# (ou que vous êtes à la racine)
try:
    from modules.diagnostic import run_diagnostic
    from modules.sauvegarde import backup_sql_pure_python, export_table_to_csv
    from modules.audit import run_audit_zabbix
except ImportError as e:
    print(f"❌ Erreur d'importation : {e}")
    print("Vérifiez que vous lancez le script depuis la racine du projet.")
    sys.exit(1)

def clear_screen():
    # Commande pour nettoyer la console (Windows ou Linux)
    os.system('cls' if os.name == 'nt' else 'clear')

def main_menu():
    while True:
        clear_screen()
        print("\n" + "═"*50)
        print("   🛠️  OUTIL D'ADMINISTRATION MSPR  🛠️")
        print("═"*50)
        print("1. 🏥 Diagnostic Infrastructure (Zabbix)")
        print("2. 💾 Sauvegarde Base de Données (SQL)")
        print("3. 📊 Export Données (CSV)")
        print("4. 🔍 Audit Obsolescence / EOL (Sécurité)")
        print("5. 🚪 Quitter")
        print("─"*50)
        
        choice = input("👉 Votre choix : ")

        if choice == "1":
            print("\n--- Lancement du Diagnostic ---")
            run_diagnostic()
            input("Appuyez sur Entrée pour continuer...")
            
        elif choice == "2":
            print("\n--- Lancement de la Sauvegarde SQL ---")
            backup_sql_pure_python()
            input("\nAppuyez sur Entrée pour continuer...")
            
        elif choice == "3":
            print("\n--- Lancement de l'Export CSV ---")
            export_table_to_csv()
            input("\nAppuyez sur Entrée pour continuer...")

        elif choice == "4":
            print("\n--- Lancement de l'Audit de Sécurité ---")
            run_audit_zabbix()
            input("\nAppuyez sur Entrée pour continuer...")
            
        elif choice == "5":
            print("\nFermeture de l'application. Au revoir !")
            break
        else:
            input("\n❌ Choix invalide. Appuyez sur Entrée...")

if __name__ == "__main__":
    main_menu()