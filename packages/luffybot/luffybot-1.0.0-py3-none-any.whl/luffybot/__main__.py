import os
import getpass

def main():
    print("🔧 Initialisation interactive de LuffyBot...\n")

    # Choix du format
    print("Choisissez la structure de l'identifiant à enregistrer dans user-password.py :")
    print("1 - (\"username\", \"password\")")
    print("2 - (\"family\", \"username\", \"password\")")
    print("3 - (\"language\", \"family\", \"username\", \"password\")")
    choix = input("Votre choix (1, 2 ou 3) : ").strip()

    if choix == "1":
        username = input("🔹 Nom d'utilisateur : ").strip()
        password = getpass.getpass("🔹 Mot de passe : ").strip()
    elif choix == "2":
        family = input("🔹 Famille (ex: vikidia) : ").strip()
        username = input("🔹 Nom d'utilisateur : ").strip()
        password = getpass.getpass("🔹 Mot de passe : ").strip()
    elif choix == "3":
        language = input("🔹 Langue (ex: fr) : ").strip()
        family = input("🔹 Famille (ex: vikidia) : ").strip()
        username = input("🔹 Nom d'utilisateur : ").strip()
        password = getpass.getpass("🔹 Mot de passe : ").strip()
    else:
        print("Choix invalide, fin du script.")
        return

    config_path = os.path.join(os.getcwd(), "user-config.py")
    password_path = os.path.join(os.getcwd(), "user-password.py")

    # On écrit user-config.py classique
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(f"""family = 'vikidia'
mylang = 'fr'
usernames['vikidia']['fr'] = '{username}'
password_file = "user-password.py"
""")

    # On écrit user-password.py avec la structure choisie
    with open(password_path, "w", encoding="utf-8") as f:
        if choix == "1":
            f.write(f"""('{username}', '{password}')\n""")
        elif choix == "2":
            f.write(f"""('{family}', '{username}', '{password}')\n""")
        else:  # choix == "3"
            f.write(f"""('{language}', '{family}', '{username}', '{password}')\n""")

    print("\n✅ Les fichiers suivants ont été créés :")
    print("   - user-config.py")
    print("   - user-password.py")
    print("N'oubliez pas de modifier votre user config et user password au besoin")
    print("🔐 Ils contiennent vos identifiants, gardez-les en sécurité !")

if __name__ == "__main__":
    main()
