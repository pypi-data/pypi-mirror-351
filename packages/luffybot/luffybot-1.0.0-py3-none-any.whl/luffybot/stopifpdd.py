import pywikibot
import time

def stop_pdd():
    # Page de discussion du bot
    discussion_page = pywikibot.Page(pywikibot.Site(), "User talk:BotHulk")

    # Récupérer la dernière révision
    last_revision = list(discussion_page.revisions(limit=1))[0]['timestamp']

    while True:
        # Attente pour éviter un trop grand nombre de requêtes
        time.sleep(5)  # Vérification toutes les minutes (tu peux ajuster la durée)

        # Récupérer la dernière révision de la page
        current_revision = list(discussion_page.revisions(limit=1))[0]['timestamp']

        # Si la page a été modifiée, arrêter le bot
        if current_revision != last_revision:
            print("La page de discussion a été modifiée. Arrêt du bot.")
            break  # Arrêt du bot

        # Sinon, continuer à exécuter le bot
        else:
            print("La page de discussion n'a pas été modifiée.")
