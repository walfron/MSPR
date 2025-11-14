def main_menu():
    while True:
        print("\n=== NTL-SysToolbox ===")
        print("1) Module Diagnostic")
        print("2) Module Sauvegarde WMS")
        print("3) Module Audit d'obsolescence")
        print("4) Quitter")

        choice = input("Votre choix : ").strip()

        if choice == "1":
            diagnostic_menu()
        elif choice == "2":
            backup_menu()
        elif choice == "3":
            audit_menu()
        elif choice == "4":
            print("Au revoir.")
            break
        else:
            print("Choix invalide, merci de réessayer.")


def diagnostic_menu():
    print("[TODO] Menu Diagnostic à implémenter")


def backup_menu():
    print("[TODO] Menu Sauvegarde à implémenter")


def audit_menu():
    print("[TODO] Menu Audit à implémenter")
