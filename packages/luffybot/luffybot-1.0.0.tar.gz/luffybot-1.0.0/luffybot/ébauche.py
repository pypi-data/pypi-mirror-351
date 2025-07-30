import pywikibot
import re
import mwparserfromhell
from datetime import datetime, timedelta

LOG_FILE = "ebauche_scan_once_log.txt"
WIKI_LOG_PAGE = "Utilisateur:LuffyBot/Logs/2025"

def log(message):
    timestamp = datetime.utcnow().strftime("[%Y-%m-%d %H:%M:%S UTC] ")
    full_message = f"* {timestamp}{message}"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(full_message + "\n")
    print(full_message)
    log_to_wiki(full_message)

def log_to_wiki(message):
    site = pywikibot.Site("fr", "vikidia")
    page = pywikibot.Page(site, WIKI_LOG_PAGE)
    try:
        old_text = page.text if page.exists() else ""
        new_text = old_text.strip() + "\n" + message
        page.text = new_text
        page.save(summary="Mise à jour automatique du journal du bot", minor=True)
    except Exception as e:
        print(f"Erreur lors de l’écriture sur la page de logs wiki : {e}")

def extract_portails(text):
    try:
        wikicode = mwparserfromhell.parse(text)
        for template in wikicode.filter_templates():
            if template.name.strip().lower() == "portail":
                # Retourne les options avec casse originale (sans forcer en minuscules)
                return [param.value.strip() for param in template.params if param.value.strip()]
    except Exception:
        raise ValueError("Texte illisible ou mal formé")
    return []

def has_ebauche(text):
    return re.search(r'\{\{\s*ébauche(?:\s*[\|\s][^}]*)?\}\}', text, re.IGNORECASE)

def has_homonymie(text):
    return re.search(r'\{\{\s*homonymie\s*\}\}', text, re.IGNORECASE)

def add_ebauche(text, options):
    if not options:
        return text
    ebauche_template = "{{ébauche|" + "|".join(options) + "}}\n"
    return ebauche_template + text

def is_too_short(text, min_words=200):
    return len(text.split()) < min_words

def main():
    site = pywikibot.Site("fr", "vikidia")
    site.login()

    since = datetime.utcnow() - timedelta(days=130)
    recent_newpages = site.recentchanges(start=since, changetype="new", namespaces=[0], reverse=True)

    for change in recent_newpages:
        title = change['title']
        page = pywikibot.Page(site, title)

        if page.isRedirectPage():
            continue

        try:
            text = page.text
        except Exception as e:
            log(f"{page.title()} ignorée : erreur de lecture → {e}")
            continue

        if has_homonymie(text):
            log(f"{page.title()} ignorée : page d’homonymie détectée")
            continue

        if not is_too_short(text):
            continue

        if has_ebauche(text):
            log(f"{page.title()} ignorée : ébauche déjà présente")
            continue

        try:
            portails = extract_portails(text)
        except ValueError:
            log(f"{page.title()} ignorée : contenu illisible ou anomalie de parsing")
            continue

        if not portails:
            log(f"{page.title()} ignorée : aucun portail détecté (à ajouter manuellement)")
            continue

        new_text = add_ebauche(text, portails)

        try:
            page.text = new_text
            page.save(summary="Ajout automatique du modèle ébauche")
            log(f"Ajout de l’ébauche sur la page {page.title()} avec les options : {', '.join(portails)}")
        except Exception as e:
            log(f"Erreur lors de la sauvegarde de {page.title()} : {e}")
            continue

    log("Scan terminé.\n")

if __name__ == "__main__":
    main()
