# 🕌 Salatime

Bot Python qui envoie des notifications Telegram **10 minutes avant chaque Iqama** pour plusieurs mosquées de Québec.

## Mosquées supportées

- CCIQ
- Masjid Annour
- Masjid Charlesbourg
- Masjid Al Athar

## Fonctionnement

1. Au démarrage, le bot scrape les horaires du jour depuis [mosqueprayertimes.com](https://mosqueprayertimes.com)
2. Il programme une notification Telegram pour chaque prière (10 min avant l'Iqama)
3. Chaque mosquée a son propre canal Telegram
4. Un message de confirmation (ou d'erreur) est envoyé à l'administrateur

## Configuration

Créer un fichier `.env` à la racine :

```
TELEGRAM_BOT_TOKEN=
ADMIN_CHAT_ID=
CANAL_CCIQ=
CANAL_CCIQ2=
CANAL_CCIQ4=
CANAL_ALATHAR=
```

## Installation

```bash
git clone https://github.com/samuelsegura/salatime.git
cd salatime
pip install -r requirements.txt
python3 salatime.py
```

## Stack

- Python 3
- `requests` — scraping + API Telegram
- `schedule` — planification des notifications
- `python-dotenv` — gestion des variables d'environnement
